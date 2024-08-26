# devTask
Python dev task

#repo
```bash
   https://github.com/risla2/devTask.git
```  

To ask
Two consumers in two enviroments with same group_id could cause restapi consumer not to read all messages at once??
[2024-08-25 21:03:59,812] INFO [GroupCoordinator 1]: Dynamic Member with unknown member id joins group dev_task in Stable state. Created a new member id kafka-python-3.0.0-94d25c56-e3c2-4f58-8291-3dc9f1e861a9 for this member and add to the group. (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:03:59 [2024-08-25 21:03:59,812] INFO [GroupCoordinator 1]: Preparing to rebalance group dev_task in state PreparingRebalance with old generation 26 (__consumer_offsets-37) (reason: Adding new member kafka-python-3.0.0-94d25c56-e3c2-4f58-8291-3dc9f1e861a9 with group instance id None; client reason: not provided) (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:01 [2024-08-25 21:04:01,541] INFO [GroupCoordinator 1]: Stabilized group dev_task generation 27 (__consumer_offsets-37) with 2 members (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:01 [2024-08-25 21:04:01,546] INFO [GroupCoordinator 1]: Assignment received from leader kafka-python-3.0.0-60415979-8b37-491c-b0c4-6a6347bcba20 for group dev_task for generation 27. The group has 2 members, 0 of which are static. (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:01 [2024-08-25 21:04:01,707] INFO [GroupCoordinator 1]: Preparing to rebalance group dev_task in state PreparingRebalance with old generation 27 (__consumer_offsets-37) (reason: Removing member kafka-python-3.0.0-94d25c56-e3c2-4f58-8291-3dc9f1e861a9 on LeaveGroup; client reason: not provided) (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:01 [2024-08-25 21:04:01,707] INFO [GroupCoordinator 1]: Member MemberMetadata(memberId=kafka-python-3.0.0-94d25c56-e3c2-4f58-8291-3dc9f1e861a9, groupInstanceId=None, clientId=kafka-python-3.0.0, clientHost=/172.19.0.5, sessionTimeoutMs=10000, rebalanceTimeoutMs=300000, supportedProtocols=List(range, roundrobin)) has left group dev_task through explicit `LeaveGroup`; client reason: not provided (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:02 [2024-08-25 21:04:02,458] INFO [GroupCoordinator 1]: Stabilized group dev_task generation 28 (__consumer_offsets-37) with 1 members (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:02 [2024-08-25 21:04:02,460] INFO [GroupCoordinator 1]: Assignment received from leader kafka-python-3.0.0-60415979-8b37-491c-b0c4-6a6347bcba20 for group dev_task for generation 28. The group has 1 members, 0 of which are static. (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:02 [2024-08-25 21:04:02,467] INFO [GroupCoordinator 1]: Preparing to rebalance group dev_task in state PreparingRebalance with old generation 28 (__consumer_offsets-37) (reason: Leader kafka-python-3.0.0-60415979-8b37-491c-b0c4-6a6347bcba20 re-joining group during Stable; client reason: not provided) (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:02 [2024-08-25 21:04:02,467] INFO [GroupCoordinator 1]: Stabilized group dev_task generation 29 (__consumer_offsets-37) with 1 members (kafka.coordinator.group.GroupCoordinator)
2024-08-25 23:04:02 [2024-08-25 21:04:02,470] INFO [GroupCoordinator 1]: Assignment received from leader kafka-python-3.0.0-60415979-8b37-491c-b0c4-6a6347bcba20 for group dev_task for generation 29. The group has 1 members, 0 of which are static. (kafka.coordinator.group.GroupCoordinator)
Fixed with 2 groups for each consumer???