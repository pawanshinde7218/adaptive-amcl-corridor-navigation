#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
import math
import statistics

class EnvironmentClassifier(Node):
    def __init__(self):
        super().__init__('env_classifier_node')
        
      
        self.current_state = "UNKNOWN"
        self.variance_threshold = 10.5  
        
     
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
            
   
        self.amcl_param_client = self.create_client(SetParameters, '/amcl/set_parameters')
        
        self.get_logger().info("Environment Classifier Node Started! Waiting for LiDAR data...")

    def scan_callback(self, msg):
        
        clean_ranges = []
        for r in msg.ranges:
            if math.isinf(r) or math.isnan(r) or r <= 0.0:
                clean_ranges.append(10.0)
            else:
                clean_ranges.append(r)
                
      
        scan_variance = statistics.variance(clean_ranges)
        
        
        if not hasattr(self, 'scan_count'): self.scan_count = 0
        self.scan_count += 1
        if self.scan_count % 15 == 0:
            self.get_logger().info(f"Shape Analysis -> Variance: {scan_variance:.2f}")

       
        if scan_variance > self.variance_threshold:
            detected_env = "CORNER"     
        else:
            detected_env = "CORRIDOR"   
            
     
        if detected_env != self.current_state:
            self.get_logger().info(f"Environment Shift! Shape changed to: {detected_env} (Variance: {scan_variance:.2f})")
            self.switch_amcl_parameters(detected_env)
            self.current_state = detected_env



    def switch_amcl_parameters(self, environment_type):
        
        while not self.amcl_param_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('AMCL parameter service not available, waiting again...')
            
        req = SetParameters.Request()
        
        if environment_type == "CORRIDOR":
            self.get_logger().info("Applying CORRIDOR Settings: Trusting EKF Odometry...")
            req.parameters = [
                self.create_param('z_hit', 0.5),       
                self.create_param('z_rand', 0.5),      
                self.create_param('alpha1', 0.002),     
                self.create_param('alpha2', 0.002),
                self.create_param('alpha3', 0.002),
                self.create_param('alpha4', 0.002)
            ]
            
        elif environment_type == "CORNER":
            self.get_logger().info("Applying CORNER Settings: Trusting LiDAR for Map Snap...")
            req.parameters = [
                self.create_param('z_hit', 0.95),      
                self.create_param('z_rand', 0.05),     
                self.create_param('alpha1', 0.05),      
                self.create_param('alpha2', 0.05),
                self.create_param('alpha3', 0.05),
                self.create_param('alpha4', 0.05)
            ]
            
       
        future = self.amcl_param_client.call_async(req)
        future.add_done_callback(self.param_set_callback)

    def create_param(self, name, value):
        param = Parameter()
        param.name = name
        param.value.type = ParameterType.PARAMETER_DOUBLE
        param.value.double_value = float(value)
        return param

    def param_set_callback(self, future):
        try:
            response = future.result()
            if all(res.successful for res in response.results):
                self.get_logger().info("AMCL Parameters Updated Successfully on-the-fly!")
            else:
                self.get_logger().warn("Some AMCL parameters failed to update.")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = EnvironmentClassifier()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Environment Classifier...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()