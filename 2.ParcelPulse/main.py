import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime
from collections import deque


class Node:
    def __init__(self,data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

def construct_kd_tree(points, depth=0):
    if not points:
        return None

    axis = depth % len(points[0])
    points.sort(key=lambda x: x[axis])

    median = len(points) // 2
    node = Node(points[median])

    node.left = construct_kd_tree(points[:median], depth + 1)
    node.right = construct_kd_tree(points[median + 1:], depth + 1)

    return node

def inorder(root):
  if not root:
    return
  inorder(root.left)
  st.write(root.data)
  inorder(root.right)

def levelorder(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []

        for level in range(level_size):
            node = queue.popleft()
            current_level.append(node.data)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result

def dist(point1,point2):
  return abs(point2[0] - point1[0]) + abs(point2[1] - point1[1])


def main():

    st.title('Parcel  Pulse')

    st.sidebar.title('Upload Files')
    uploaded_file_xlsx = st.sidebar.file_uploader("Upload Kitchen data (XLSX file)", type=["xlsx"])
    uploaded_file_txt = st.sidebar.file_uploader("Upload Riders data (TXT file)", type=["txt"])

    if st.sidebar.button("Submit"):
        if uploaded_file_xlsx is not None and uploaded_file_txt is not None:
            
            df = pd.read_excel(uploaded_file_xlsx)
            #st.write(df)

            content = uploaded_file_txt.getvalue().decode("utf-8")
            rider_list=content.split("#")

            for i in range(len(rider_list)):
                rider_list[i]=rider_list[i].strip()
            #st.write(rider_list)

            customer_details={}
            for i in range(len(df["customer_name"])):
                customer_location=tuple(map(int,df["customer_location"][i][1:-1].split(',')))
                customer_details[df["customer_name"][i]]=customer_location
            
            kitchen_details={}
            for i in range(len(df["kitchen_name"])):
                kitchen_location=tuple(map(int,df["kitchen_location"][i][1:-1].split(',')))
                kitchen_details[df["kitchen_name"][i]]=kitchen_location

            kitchen_customer_location_values=list(customer_details.values())+list(kitchen_details.values())
            kitchen_customer_root = construct_kd_tree(kitchen_customer_location_values)
            

            customer_order=defaultdict(list)
            for i in range(len(df["customer_name"])):
                customer_order[df["customer_name"][i]].append(df["order_id"][i])

            order_details=defaultdict(dict)
            for i in range(len(df["order_id"])):
                order_details[df["order_id"][i]]["ready_time"]=(df["ready_time"][i])
                order_details[df["order_id"][i]]["kitchen_name"]=(df["kitchen_name"][i])
                order_details[df["order_id"][i]]["customer_name"]=(df["customer_name"][i])

            kitchen_order=defaultdict(list)
            for i in range(len(df["kitchen_name"])):
                kitchen_order[df["kitchen_name"][i]].append(df["order_id"][i])

            def find_path(root, source, destination):
                def dfs(node, target, path):
                    if not node:
                        return False, []

                    path.append(node.data)

                    if node.data == target:
                        return True, path

                    found_left, left_path = dfs(node.left, target, path.copy())
                    if found_left:
                        return True, left_path

                    found_right, right_path = dfs(node.right, target, path.copy())
                    if found_right:
                        return True, right_path

                    return False, []

                found1, path1 = dfs(root, source, [])
                found2, path2 = dfs(root, destination, [])

                if found1 and found2:
                    return path1, path2
                else:
                    return [], []

            def path_through_kitchen(source,through,destination):
                path1, path2=find_path(kitchen_customer_root,kitchen_details[source],customer_details[destination])
                if path1 and path2:
                    i=0
                    j=0
                    while i<len(path1) and j<len(path2) and path1[i]==path2[j]:
                        i+=1
                        j+=1
                    path_source_destination=path1[i-1:] + path2[j:]
                    if kitchen_details[through] in path_source_destination:
                        return True
                    else:
                        return False
                else:
                    return False

            def path_through_customer(source,through,destination):
                path1, path2=find_path(kitchen_customer_root,kitchen_details[source],customer_details[destination])
                if path1 and path2:
                    i=0
                    j=0
                    while i<len(path1) and j<len(path2) and path1[i]==path2[j]:
                        i+=1
                        j+=1
                    path_source_destination=path1[i-1:] + path2[j:]
                    if customer_details[through] in path_source_destination:
                        return True
                    else:
                        return False
                else:
                    return False

            def path_through_kitchen_customer(kitchen1,kitchen2,customer1,customer2):
                path1, path2=find_path(kitchen_customer_root,kitchen_details[kitchen1],customer_details[customer2])
                if path1 and path2:
                    i=0
                    j=0
                    while i<len(path1) and j<len(path2) and path1[i]==path2[j]:
                        i+=1
                        j+=1
                    path_source_destination=path1[i-1:] + path2[j:]
                    if kitchen_details[kitchen2] in path_source_destination:
                        if customer_details[customer1] in path_source_destination:
                            return True
                return False
            
            #Combination of rule 1 and rule 2 and rule 6
            order_rider=defaultdict(dict)
            j=0
            for i in customer_order:
                j+=1
                if j>=len(rider_list):
                    j=j%len(rider_list)
                if len(customer_order[i])>1:
                    order_rider[customer_order[i][0]]["rider"]=rider_list[j]
                    order_rider[customer_order[i][0]]["ready_time"]=order_details[customer_order[i][0]]["ready_time"]
                    for order_id in customer_order[i]:
                        order_ready_list=list(order_rider.values())
                        order_id_list=list(order_rider.keys())
                        last_order=order_ready_list[-1]
                        last_order_ready=last_order["ready_time"]
                        last_order_rider=last_order["rider"]
                        distance_between=dist(kitchen_details[order_details[order_id]["kitchen_name"]],kitchen_details[order_details[order_id_list[-1]]["kitchen_name"]])
                        if (order_details[order_id]["kitchen_name"]==order_details[order_id_list[-1]]["kitchen_name"]) or (distance_between<=1):
                            today = datetime.datetime.today()
                            datetime1 = datetime.datetime.combine(today, last_order_ready)
                            datetime2 = datetime.datetime.combine(today, order_details[order_id]["ready_time"])
                            if abs(datetime1 - datetime2).total_seconds()/60<=10:
                                order_rider[order_id]["rider"]=last_order_rider
                                order_rider[order_id]["ready_time"]=order_details[order_id]["ready_time"]
                                continue
                        elif (order_details[order_id]["kitchen_name"]!=order_details[order_id_list[-1]]["kitchen_name"]) and (path_through_kitchen(order_details[order_id]["kitchen_name"],order_details[order_id_list[-1]]["kitchen_name"],i)):
                            today = datetime.datetime.today()
                            datetime1 = datetime.datetime.combine(today, last_order_ready)
                            datetime2 = datetime.datetime.combine(today, order_details[order_id]["ready_time"])
                            duration=abs(datetime1 - datetime2).total_seconds()/60
                            if  duration <= 10 or duration <= 10*(distance_between):
                                order_rider[order_id]["rider"]=last_order_rider
                                order_rider[order_id]["ready_time"]=order_details[order_id]["ready_time"]
                                continue
                        if order_id_list[-1]==order_id:
                            continue
                        j+=1
                        if j>=len(rider_list):
                            j=j%len(rider_list)
                        order_rider[order_id]["rider"]=rider_list[j]
                        order_rider[order_id]["ready_time"]=order_details[order_id]["ready_time"]
                    j+=1
                    if j>=len(rider_list):
                        j=j%len(rider_list)
                else:
                    order_rider[customer_order[i][0]]["rider"]=rider_list[j]
                    order_rider[customer_order[i][0]]["ready_time"]=order_details[customer_order[i][0]]["ready_time"]
                    j+=1
                    if j>=len(rider_list):
                        j=j%len(rider_list)


            #Rule 7

            order_rider_rule_7=defaultdict(dict)
            j=0
            for i in order_details:
                if j>=len(rider_list):
                    j=j%len(rider_list)
                order_rider_list=list(order_rider_rule_7.keys())
                if len(order_rider_list)==0 or i not in order_rider_list:
                    order_rider_rule_7[i]["rider"]=rider_list[j]
                    order_rider_rule_7[i]["ready_time"]=order_details[i]["ready_time"]
                for k in order_details:
                    j+=1
                    if j>=len(rider_list):
                        j=j%len(rider_list)
                    distance_between_kitchen=dist(kitchen_details[order_details[k]["kitchen_name"]],kitchen_details[order_details[i]["kitchen_name"]])
                    distance_between_customers=dist(customer_details[order_details[k]["customer_name"]],customer_details[order_details[i]["customer_name"]])
                    if distance_between_customers > 0 and distance_between_kitchen > 0 and(path_through_kitchen_customer(order_details[i]["kitchen_name"],order_details[k]["kitchen_name"],order_details[i]["customer_name"],order_details[k]["customer_name"]) or path_through_kitchen_customer(order_details[k]["kitchen_name"],order_details[i]["kitchen_name"],order_details[k]["customer_name"],order_details[i]["customer_name"])):
                        today = datetime.datetime.today()
                        datetime1 = datetime.datetime.combine(today, order_rider_rule_7[i]["ready_time"])
                        datetime2 = datetime.datetime.combine(today, order_details[k]["ready_time"])
                        duration=abs(datetime1 - datetime2).total_seconds()/60
                        if  duration <= 10 or duration <= 10*(distance_between_kitchen):
                            order_rider_rule_7[k]["rider"]=order_rider_rule_7[i]["rider"]
                            order_rider_rule_7[k]["ready_time"]=order_details[k]["ready_time"]
                            order_rider[order_id_list[-1]]["rider"]=order_rider_rule_7[i]["rider"]
                            order_rider[order_id_list[-1]]["ready_time"]=order_details[order_id]["ready_time"]
                            order_rider[order_id]["rider"]=order_rider_rule_7[i]["rider"]
                            order_rider[order_id]["ready_time"]=order_details[order_id]["ready_time"]
                            continue
                    if distance_between_customers==0 or distance_between_kitchen == 0:
                        continue
                    else:
                        j+=1
                        if j>=len(rider_list):
                            j=j%len(rider_list)
                        order_rider_rule_7[k]["rider"]=rider_list[j]
                        order_rider_rule_7[k]["ready_time"]=order_details[k]["ready_time"]

            
            #Combination of rule 3 and rule 8

            order_rider_rule_8=defaultdict(dict)
            j=0
            for i in kitchen_order:
                j+=1
                if j>=len(rider_list):
                    j=j%len(rider_list)
                if len(kitchen_order[i])>1:
                    order_rider_rule_8[kitchen_order[i][0]]["rider"]=rider_list[j]
                    order_rider_rule_8[kitchen_order[i][0]]["ready_time"]=order_details[kitchen_order[i][0]]["ready_time"]
                    for order_id in kitchen_order[i]:
                        if j>=len(rider_list):
                            j=j%len(rider_list)
                        order_ready_list=list(order_rider_rule_8.values())
                        order_id_list=list(order_rider_rule_8.keys())
                        last_order=order_ready_list[-1]
                        last_order_ready=last_order["ready_time"]
                        last_order_rider=last_order["rider"]
                        distance_between=dist(customer_details[order_details[order_id]["customer_name"]],customer_details[order_details[order_id_list[-1]]["customer_name"]])
                        if (order_details[order_id]["customer_name"]!=order_details[order_id_list[-1]]["customer_name"]) and (distance_between<=1 or (path_through_customer(i,order_details[order_id]["customer_name"],order_details[order_id_list[-1]]["customer_name"]) or path_through_customer(i,order_details[order_id_list[-1]]["customer_name"],order_details[order_id]["customer_name"]))):
                            today = datetime.datetime.today()
                            datetime1 = datetime.datetime.combine(today, last_order_ready)
                            datetime2 = datetime.datetime.combine(today, order_details[order_id]["ready_time"])
                            if abs(datetime1 - datetime2).total_seconds()/60<=10:
                                order_rider_rule_8[order_id]["rider"]=last_order_rider
                                order_rider_rule_8[order_id]["ready_time"]=order_details[order_id]["ready_time"]
                                order_rider[order_id_list[-1]]["rider"]=last_order_rider
                                order_rider[order_id_list[-1]]["ready_time"]=order_details[order_id]["ready_time"]
                                order_rider[order_id]["rider"]=last_order_rider
                                order_rider[order_id]["ready_time"]=order_details[order_id]["ready_time"]
                                continue
                        if order_id_list[-1]==order_id:
                            continue
                        j+=1
                        if j>=len(rider_list):
                            j=j%len(rider_list)
                        order_rider_rule_8[order_id]["rider"]=last_order_rider
                        order_rider_rule_8[order_id]["ready_time"]=order_details[order_id]["ready_time"]
                    j+=1
                    if j>=len(rider_list):
                        j=j%len(rider_list)
                else:
                    order_rider_rule_8[kitchen_order[i][0]]["rider"]=rider_list[j]
                    order_rider_rule_8[kitchen_order[i][0]]["ready_time"]=order_details[kitchen_order[i][0]]["ready_time"]
                    j+=1
                    if j>=len(rider_list):
                        j=j%len(rider_list)


            rider_assignment=defaultdict(list)
            for i in order_rider:
                rider_assignment[order_rider[i]["rider"]].append(i)
                
            st.subheader("Assignment of Riders")
            for i in rider_assignment:
                rider_assignemnt_order=defaultdict(dict)
                for j in order_details:
                    if j in rider_assignment[i]:
                        rider_assignemnt_order[j]["customer_name"]=order_details[j]["customer_name"]
                        rider_assignemnt_order[j]["Kitchen_name"]=order_details[j]["kitchen_name"]
                st.subheader(f"Rider name: {i}")
                st.table(rider_assignemnt_order)
                
            
            
if __name__ == "__main__":
    main()