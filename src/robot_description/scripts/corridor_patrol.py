#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PointStamped, PoseStamped
from nav2_msgs.action import NavigateToPose
import math

class CorridorPatrolNode(Node):
    def __init__(self):
        super().__init__('corridor_patrol_node')
        
      
        self.subscription = self.create_subscription(
            PointStamped,
            '/clicked_point',
            self.point_callback,
            10)
            
        
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.points = []
        self.current_target_index = 0
        self.is_patrolling = False
        
        self.get_logger().info("Patrol Node Started!")
        self.get_logger().info("Please click EXACTLY 2 points in RViz using the 'Publish Point' tool.")

    def point_callback(self, msg):
        if self.is_patrolling:
            self.get_logger().warn("Robot is already patrolling. Ignoring new clicks.")
            return
            
        self.points.append(msg)
        self.get_logger().info(f"Point {len(self.points)} saved: x={msg.point.x:.2f}, y={msg.point.y:.2f}")
        
       
        if len(self.points) == 2:
            self.get_logger().info("Both points received! Starting infinite patrol loop...")
            self.is_patrolling = True
            self.send_next_goal()

    def get_orientation_to_target(self, start_pt, target_pt):
      
        dy = target_pt.point.y - start_pt.point.y
        dx = target_pt.point.x - start_pt.point.x
        yaw = math.atan2(dy, dx)
        
  
        qz = math.sin(yaw / 2.0)
        qw = math.cos(yaw / 2.0)
        return qz, qw

    def send_next_goal(self):
      
        self.nav_client.wait_for_server()
        
        target_point = self.points[self.current_target_index]
        start_point = self.points[(self.current_target_index + 1) % 2]
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = target_point.header.frame_id
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
       
        goal_msg.pose.pose.position.x = target_point.point.x
        goal_msg.pose.pose.position.y = target_point.point.y
        goal_msg.pose.pose.position.z = 0.0
        
       
        qz, qw = self.get_orientation_to_target(start_point, target_point)
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw
        
        point_name = "A" if self.current_target_index == 0 else "B"
        self.get_logger().info(f"Navigating to Point {point_name}...")
        
       
        self.send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Nav2 rejected the goal!")
            return
            
        self.get_logger().info("Goal accepted by Nav2. Moving...")
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        status = future.result().status
        self.get_logger().info(f"Destination reached! (Status code: {status})")
        
        
        self.current_target_index = (self.current_target_index + 1) % 2
        
      
        self.send_next_goal()

def main(args=None):
    rclpy.init(args=args)
    node = CorridorPatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Patrol stopped by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()