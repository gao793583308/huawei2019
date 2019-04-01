import sys
import random
import time

def read_data(road_path, cross_path):
    Cross_info = open(cross_path).readlines()
    Cross = {}
    for item in Cross_info[1:]:
        cross_id, road1, road2, road3, road4 = [int(i) for i in item.strip()[1:-1].split(",")]
        Cross[cross_id] = [road1, road2, road3, road4]

    Road_info = open(road_path).readlines()
    Road = {}
    Map = {}

    for item in Road_info[1:]:
        road_id, road_len, road_max_v, road_num_path, begin_id, end_id, mul_path = [int(i) for i in
                                                                                    item.strip()[1:-1].split(",")]

        Road[road_id] = {'road_len': road_len, 'road_max_v': road_max_v, 'road_num_path': road_num_path,
                         'mul_path': mul_path}

        if (begin_id not in Map):
            Map[begin_id] = {end_id: road_id}
        else:
            if (end_id not in Map[begin_id]):
                Map[begin_id][end_id] = road_id
            else:
                print("wrong_dul_data")

        if (mul_path):
            if (end_id not in Map):
                Map[end_id] = {begin_id: road_id}
            else:
                if (begin_id not in Map[end_id]):
                    Map[end_id][begin_id] = road_id
                else:
                    print("wrong_dul_data")

    return Cross, Road, Map


def ini_Path(road_path):
    Road_info = open(road_path).readlines()
    Path = {}
    for item in Road_info[1:]:
        road_id, road_len, road_max_v, road_num_path, begin_id, end_id, mul_path = [int(i) for i in
                                                                                    item.strip()[1:-1].split(",")]

        if (end_id not in Path):
            Path[end_id] = {road_id: [[] for i in range(road_num_path)]}
        else:
            Path[end_id][road_id] = [[] for i in range(road_num_path)]

        if (mul_path):
            if (begin_id not in Path):
                Path[begin_id] = {road_id: [[] for i in range(road_num_path)]}
            else:
                Path[begin_id][road_id] = [[] for i in range(road_num_path)]
    return Path


def ini_carport(car_path, Map):
    Carport_total = {}
    Car_info = open(car_path).readlines()
    for item in Car_info[1:]:
        car_id, begin_id, end_id, max_v, begin_time = [int(i) for i in item.strip()[1:-1].split(",")]
        car = {'car_id': car_id, 'begin_id': begin_id,'end_id': end_id, 'max_v': max_v, 'begin_time': begin_time, 'state': -1, 's1': -1,
              'direction': 'unknow', 'next_cross': -1, 'should_judge': 1}
        Carport_total[car_id] = car
    return Carport_total


def cal_dis(Map, Road):
    Dist = {}
    path_detail = {}
    roadid_list = list(Map.keys())
    for cross_id1 in roadid_list:
        for cross_id2 in roadid_list:
            if (cross_id1 not in Dist):
                Dist[cross_id1] = {cross_id2: float("inf")}
            elif (cross_id2 not in Dist[cross_id1]):
                Dist[cross_id1][cross_id2] = float("inf")
            if (cross_id1 not in path_detail):
                path_detail[cross_id1] = {cross_id2: [cross_id1]}
            elif (cross_id2 not in path_detail[cross_id1]):
                path_detail[cross_id1][cross_id2] = [cross_id1]

    for cross_id1 in Map:
        for cross_id2 in Map[cross_id1]:
            Dist[cross_id1][cross_id2] = Road[Map[cross_id1][cross_id2]]['road_len']
            path_detail[cross_id1][cross_id2] = [cross_id1,cross_id2]

    for k in range(len(roadid_list)):
        Dist[roadid_list[k]][roadid_list[k]] = 0

    for k_index in range(len(roadid_list)):
        k = roadid_list[k_index]
        for i_index in range(len(roadid_list)):
            i = roadid_list[i_index]
            for j_index in range(len(roadid_list)):
                j = roadid_list[j_index]
                if (Dist[i][k] < float("inf") and Dist[k][j] < float("inf") and Dist[i][j] > Dist[i][k] + Dist[k][j]):
                    path_detail[i][j] = list(path_detail[i][k]) + list(path_detail[k][j][1:])
                    Dist[i][j] = Dist[i][k] + Dist[k][j]
    return Dist, path_detail


def Still_have_cars(Path, Carport_toatl, Carport):
    if(Carport_toatl):
        return 1
    #---------------check car in road----------------------
    for cross_id in Path:
        for road_id in Path[cross_id]:
            for drive_way in Path[cross_id][road_id]:
                if(drive_way):
                    return 1
    #---------------check car in carport--------------------
    for cross_id in Carport:
        if(Carport[cross_id]):
            return 1
    return 0


def Dispatch_cars(Path, Map, Road, Distance, Cross):
    for cross_id in Path:
        for road_id in Path[cross_id]:
            for drive_way in Path[cross_id][road_id]:
                for car in drive_way:
                    if(car['should_judge'] == 0):
                        car['state'] = 0
                        continue

                    if(car['end_id'] == cross_id):
                        car['state'] = 0
                        car['direction'] = 'D'
                    else:
                        S = float('inf')
                        final_cross_id = -1
                        final_road_id = -1
                        for next_cross_id in Map[cross_id]:
                            next_road_id = Map[cross_id][next_cross_id]

                            if(next_road_id == road_id):
                                continue
                            else:
                                #now_dis = Distance[next_cross_id][car['end_id']] + Road[next_road_id]['road_len']
                                now_dis = Distance[next_cross_id][car['end_id']] + Road[next_road_id]['road_len']
                                num_car_in_path = 0

                                for way in Path[next_cross_id][next_road_id]:
                                    num_car_in_path = num_car_in_path + len(way)
                                # s_new = s_new + num_car_in_path
                                road_full = num_car_in_path / (Road[next_road_id]['road_len'] * Road[next_road_id]['road_num_path'])
                                now_dis = now_dis *(3+road_full)

                                if(now_dis < S):
                                    S = now_dis
                                    final_cross_id = next_cross_id
                                    final_road_id = next_road_id
                        car['state'] = 0
                        car['next_cross'] = final_cross_id
                        index1 = Cross[cross_id].index(road_id)
                        index2 = Cross[cross_id].index(final_road_id)
                        if (abs(index1 - index2) == 2):
                            car['direction'] = 'D'
                        elif (index1 - index2 == -1 or index1 - index2 == 3):
                            car['direction'] = 'L'
                        else:
                            car['direction'] = 'R'
                    car['should_judge'] = 0



def process_drive_way(drive_way, Road, Map, road_id, cross_id):
    for car in drive_way:
        if (car['state'] == 2):
            continue
        v_car = min(car['max_v'], Road[road_id]['road_max_v'])
        car_index = drive_way.index(car)
        # ------------to arrived car---------------------

        if (car['s1'] < v_car):
            if (car_index == 0 or drive_way[car_index - 1]['state'] != 2):
                car['state'] = 1
            elif (drive_way[car_index - 1]['state'] == 2):
                car['s1'] = drive_way[car_index - 1]['s1'] + 1
                car['state'] = 2
            else:
                print("wrong 1")
        else:

            if (car_index == 0 or (car['s1'] - drive_way[car_index - 1]['s1'] - 1 >= v_car)):
                car['s1'] = max(0, car['s1'] - v_car)
                if(car['s1'] < 0):
                    print("s1 value wrong")
                car['state'] = 2
            else:
                if (drive_way[car_index - 1]['state'] == 2):
                    car['s1'] = drive_way[car_index - 1]['s1'] + 1
                    car['state'] = 2
                else:
                    car['state'] = 0
    #while(drive_way and drive_way[0]['direction'] == 'to_arrived' and drive_way[0]['s1'] < 0):
        #drive_way.pop(0)

def Look_all_driveway(Path, Road, Map):
    for cross_id in Path:
        for road_id in Path[cross_id]:
            for drive_way in Path[cross_id][road_id]:
                process_drive_way(drive_way, Road, Map, road_id, cross_id)



def Do_not_process_all_cars(Path):
    for cross_id in Path:
        for road_id in Path[cross_id]:
            for drive_way in Path[cross_id][road_id]:
                for car in drive_way:
                    if(car['state'] != 2):
                        return 1
    return 0


def find_fist_order(car_list, dir):
        result_i, result_j = -1, -1
        s1 = float('inf')
        for i in range(len(car_list)):
            for j in range(len(car_list[i])):
                if (car_list[i][j]['state'] == 2 or car_list[i][j]['state'] == 0):
                    break
                else:
                    if (car_list[i][j]['s1'] < s1):
                        s1 = car_list[i][j]['s1']
                        result_i, result_j = i, j
                    break
        if(dir):
            if(result_i != -1 and result_j != -1):
                return car_list[result_i][result_j]['direction']
            else:
                return 0
        else:
            return result_i, result_j


def Look_all_cross(Path, Cross, Map, Road, T):
    dead_lock = 1
    for cross_id in sorted(Path.keys()):
        road_id_list = list(Path[cross_id].keys())
        road_id_list = sorted(road_id_list)
        index_list = []
        for road_id in road_id_list:
            index_list.append(Cross[cross_id].index(road_id))
            i = 0
        while(i < len(road_id_list)):
            road_id = road_id_list[i]
            position = Cross[cross_id].index(road_id)
            car_list = Path[cross_id][road_id]
            car_i, car_j = find_fist_order(car_list, 0)
            if (car_i == -1 and car_j == -1):
                i = i + 1
                continue

            car = car_list[car_i][car_j]
            if (car['end_id'] == cross_id):
                car_list[car_i].pop(car_j)
                dead_lock = 0
                all_time.append(T - car['begin_time'])
                process_drive_way(car_list[car_i], Road, Map, road_id, cross_id)
                continue

            flag = 0
            if (car['direction'] == 'D'):
                flag = 1
            elif (car['direction'] == 'L'):
                new_position = (position + 3) % 4

                if (new_position not in index_list):
                    flag = 1
                else:
                    new_roadid = Cross[cross_id][new_position]
                    if(find_fist_order(Path[cross_id][new_roadid],1) != "D"):
                        flag = 1
            elif (car['direction'] == "R"):
                new_position1 = (position + 1) % 4
                new_position2 = (position + 2) % 4
                if(new_position1 not in index_list or
                        find_fist_order(Path[cross_id][Cross[cross_id][new_position1]],1) != "D"):
                    if (new_position2 not in index_list or
                            find_fist_order(Path[cross_id][Cross[cross_id][new_position2]], 1) != "L"):
                        flag = 1

            if(flag):
                next_cross = car['next_cross']
                next_road = Map[cross_id][next_cross]
                road_max_v = Road[next_road]['road_max_v']
                length = Road[next_road]['road_len']

                count = -1
                s2 = min(car['max_v'], road_max_v) - car['s1']
                if(s2 <= 0):
                    car['s1'] = 0
                    car['state'] = 2
                    dead_lock = 0
                    process_drive_way(Path[cross_id][road_id][car_i], Road, Map, road_id, cross_id)
                else:
                    for each_path in Path[next_cross][next_road]:
                        count = count + 1
                        if (not each_path or each_path[-1]['s1'] < length - s2):
                            car['state'] = 2
                            dead_lock = 0
                            car['s1'] = length - s2
                            car['should_judge'] = 1
                            each_path.append(car)
                            result[car['car_id']].append(next_road)
                            Path[cross_id][road_id][car_i].pop(car_j)
                            process_drive_way(Path[cross_id][road_id][car_i], Road, Map, road_id, cross_id)
                            break
                        else:
                            if (each_path[-1]['state'] == 2):
                                if (each_path[-1]['s1'] < length - 1):
                                    car['s1'] = each_path[-1]['s1'] + 1
                                    car['state'] = 2
                                    dead_lock = 0
                                    car['should_judge'] = 1
                                    each_path.append(car)
                                    result[car['car_id']].append(next_road)
                                    Path[cross_id][road_id][car_i].pop(car_j)
                                    process_drive_way(Path[cross_id][road_id][car_i], Road, Map, road_id, cross_id)
                                    break
                                else:
                                    if (count == len(Path[next_cross][next_road]) - 1):
                                        car['s1'] = 0
                                        car['state'] = 2
                                        dead_lock = 0
                                        process_drive_way(Path[cross_id][road_id][car_i], Road, Map, road_id, cross_id)
                                    else:
                                        continue
                            else:
                                i = i + 1
                                break
            else:
                i = i + 1
    return dead_lock



def Look_all_carport(Carport, Path, Limit_number, T, Map, Distance, Road, have_stated_car, car_v_record):
    max_v = -1
    for v in sorted(car_v_record.keys(), reverse=True):
        if(car_v_record[v] > 0):
            max_v = v
            break
    #print(car_v_record)

    for cross_id in Carport:
        if(count_car(Path) > Limit_number):
            break
        #print(Carport[cross_id])
        pop_list = []
        cnt = 0
        for i in range(len(Carport[cross_id])):
            car = Carport[cross_id][i]
            if(car['max_v'] != max_v):
                continue
            result[car['car_id']] = [T]
            S = float('inf')
            final_cross = -1
            final_road = -1

            for can_dir in Map[cross_id]:
                next_roadid = Map[cross_id][can_dir]
                now_dis = Distance[can_dir][car['end_id']] + Road[next_roadid]['road_len']
                num_car_in_path = 0
                for way in Path[can_dir][next_roadid]:
                    num_car_in_path = num_car_in_path + len(way)
                # s_new = s_new + num_car_in_path
                road_full = num_car_in_path / (Road[next_roadid]['road_len'] * Road[next_roadid]['road_num_path'])
                #now_dis = now_dis * (2 + road_full)
                if (now_dis < S):
                    S = now_dis
                    final_cross = can_dir
                    final_road = next_roadid

            length = Road[final_road]['road_len']
            road_max_v =Road[final_road]['road_max_v']
            for each_path in Path[final_cross][final_road]:
                if (not each_path):
                    car['state'] = 2
                    car['s1'] = length - min(car['max_v'], road_max_v)
                    pop_list.append(i)
                    each_path.append(car)
                    cnt = cnt + 1
                    result[car['car_id']].append(final_road)
                    car_v_record[max_v] = car_v_record[max_v] - 1
                    break
                elif (each_path[-1]['s1'] <= length - 2):
                    #if (each_path[-1]['max_v'] < car['max_v']):
                        #break
                    car['state'] = 2
                    car['s1'] = max(length - min(car['max_v'], road_max_v),
                                                each_path[-1]['s1'] + 1)
                    pop_list.append(i)
                    each_path.append(car)
                    cnt = cnt + 1
                    result[car['car_id']].append(final_road)
                    car_v_record[max_v] = car_v_record[max_v] - 1
                    break
                else:
                    continue

        for i in range(len(pop_list)-1, -1, -1):
            have_stated_car.add(Carport[cross_id][pop_list[i]]['car_id'])
            Carport[cross_id].pop(pop_list[i])



def count_car(Path):
    num_car = 0
    for cross in Path:
        for road_id in Path[cross]:
            for drive_way in Path[cross][road_id]:
                num_car = num_car + len(drive_way)
    return num_car


def out_put_all_cars(Path):
    for cross_id in Path:
        for road_id in Path[cross_id]:
            for drive_way in Path[cross_id][road_id]:
                for car in drive_way:
                    print(cross_id, car)
    #print("\n")


def Put_car_in_carport(Carport, Carport_total, T, car_v_record):
    while(Carport_total and Carport_total[0]['begin_time'] <= T):
        car = Carport_total[0]
        Carport[car['begin_id']].append(car)
        if(car['max_v'] not in car_v_record):
            car_v_record[car['max_v']] = 1
        else:
            car_v_record[car['max_v']] = car_v_record[car['max_v']] + 1
        Carport_total.pop(0)

    for key in Carport:
        Carport[key] = sorted(Carport[key], key = lambda d:d['car_id'])


def process_dead_lock(Path, have_stated_car, path_record, T, Carport_total):
    stop_road = {}
    for cross_id in Path:
        for road_id in Path[cross_id]:
            for drive_way in Path[cross_id][road_id]:
                for car in drive_way:
                    if(car['state'] != 2):
                        if(cross_id != car['next_cross']):
                            beign_id, end_id = cross_id, car['next_cross']
                            if(beign_id not in stop_road):
                                stop_road[beign_id] = {end_id: [car['car_id']]}
                            else:
                                if(end_id not in stop_road[beign_id]):
                                    stop_road[beign_id][end_id] = [car['car_id']]
                                else:
                                    stop_road[beign_id][end_id].append(car['car_id'])
    possible_delay_car = set()
    delay_car = set()
    for cross_id1 in stop_road:
        for cross_id2 in stop_road[cross_id1]:
            if(cross_id1 in path_record and cross_id2 in path_record[cross_id1]):
                possible_delay_car = possible_delay_car| set(path_record[cross_id1][cross_id2])
                v_car = [[i, Carport_total[i]['max_v']] for i in stop_road[cross_id1][cross_id2]]
                v_car = sorted(v_car, key = lambda d:d[1])
                #print(v_car)
                delete_car = [v_car[i][0] for i in range(int(len(v_car)/2))]
                delay_car = delay_car | set(delete_car)
    possible_delay_car = (possible_delay_car - have_stated_car)|delay_car
    #possible_delay_car = delay_car
    for car_id in possible_delay_car:
        if(Carport_total[car_id]['begin_time'] < T):
            Carport_total[car_id]['begin_time'] = T


result = {}
all_time = []
def main():
    #-------------------read data----------------------------
    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    answer_path = sys.argv[4]
    start = time.time()



    #car_path, road_path, cross_path, answer_path = ['../data/1-map-training-2/car.txt', '../data/1-map-training-2/road.txt', '../data/1-map-training-2/cross.txt', '../data/1-map-training-2/answer.txt']

    #car_path, road_path, cross_path, answer_path = ['../data/1-map-training-1/car.txt','../data/1-map-training-1/road.txt','../data/1-map-training-1/cross.txt','../data/1-map-training-1/answer.txt']

    #car_path, road_path, cross_path, answer_path = ['../data/test/car.txt','../data/test/road.txt','../data/test/cross.txt','../data/test/answer.txt']
    #car_path, road_path, cross_path, answer_path = ['../data/1-map-training-3/car.txt','../data/1-map-training-3/road.txt','../data/1-map-training-3/cross.txt','../data/1-map-training-3/answer.txt']
    #car_path, road_path, cross_path, answer_path = ['../data/1-map-exam-1/car.txt','../data/1-map-exam-1/road.txt','../data/1-map-exam-1/cross.txt','../data/1-map-exam-1/answer.txt']

    Cross, Road, Map = read_data(road_path, cross_path)
    #-----------------ini carport-----------------------------
    Carport_total= ini_carport(car_path, Map)
    # -----------------calculate distance between two cross.
    Distance, path_detail = cal_dis(Map, Road)
    possible_path = {}
    for car_id in Carport_total:
        car = Carport_total[car_id]
        begin_id, end_id, car_id = car['begin_id'], car['end_id'], car['car_id']
        s_detail = path_detail[begin_id][end_id]
        for i in range(len(s_detail) - 1):
            first, second = s_detail[i], s_detail[i + 1]
            if (first not in possible_path):
                possible_path[first] = {second: [car_id]}
            else:
                if (second not in possible_path[first]):
                    possible_path[first][second] = [car_id]
                else:
                    possible_path[first][second].append(car_id)

    #----------------reset parameter--------------------------
    dead_lock = 1
    while(dead_lock == 1):
        Path = ini_Path(road_path)
        Carport_temp = []
        for car_id in Carport_total:
            Carport_temp.append(Carport_total[car_id].copy())
        Carport_temp = sorted(Carport_temp, key = lambda d: d['begin_time'])
        Carport = {}
        for key in Map:
            Carport[key] = []

        #-----------------Start scheduling------------------------
        T = 0
        dead_lock = 0
        have_stated_car = set()
        car_v_record = {}
        all_time = []
        while(Still_have_cars(Path, Carport_temp, Carport) and dead_lock != 1):
            T = T + 1
            #print(T, count_car(Path))
            #all_car_time = all_car_time + count_car(Path)
            #------------------------Dispatching cars------------------
            Dispatch_cars(Path, Map, Road, Distance, Cross)
            #out_put_all_cars(Path)
            #a = input()
            Look_all_driveway(Path, Road, Map)

            while(Do_not_process_all_cars(Path)):
                dead_lock = Look_all_cross(Path, Cross, Map, Road, T)
                if(dead_lock):
                    print("dead lock happen at " + str(T) + ", " + str(len(have_stated_car)) + " cars have start")
                    process_dead_lock(Path, have_stated_car, possible_path, T, Carport_total)
                    break

            #-----------------------Put car in carport-----------------
            if(count_car(Path) < 2000):
                Put_car_in_carport(Carport, Carport_temp, T, car_v_record)
                Look_all_carport(Carport, Path, 3500, T, Map, Distance, Road, have_stated_car, car_v_record)
        #out_put_all_cars(Path)
        #A = input()
    #print(all_car_time)
    #---------write result
    print(sum(all_time))
    print("final T is ", T)
    num = len(result)
    result_file = open(answer_path, "w")
    result_file.write("#(carId,StartTime,RoadId...)\n")
    cnt = 0
    for car in sorted(result.keys()):
        cnt = cnt + 1
        result_file.write("(")
        result_file.write(str(car))
        for road in result[car]:
            result_file.write(", " + str(road))
        result_file.write(")")
        if (cnt != num):
            result_file.write("\n")

    # long running

    end = time.time()

    print(end - start)



if __name__ == "__main__":
    main()

