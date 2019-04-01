# 华为2019软件精英挑战赛--初赛33名
### <a href = "https://codecraft.huawei.com/Generaldetail">赛题介绍</a>
### 队伍名称：TestNWPU
### 队员:高轶群，曹悦
        ./src/CodeCraft-2019.py 是调度代码
        ./data/ 存放着数据
        运行方式：python3 CodeCraft-2019.py ../data/1-map-exam-1/car.txt ../data/1-map-exam-1/road.txt ../data/1-map-exam-1/cross.txt ../data/1-map-exam-1/answer.txt
        上传的这一版代码最终分数是3400。
### 整体思路
### 1.车辆路径选择问题

我们首先考虑所有车辆走最短的路径，然后动态的调整车辆的出发时间来降低整体的调度时间，但是在实际实验中发现车辆走最短路径存在着死锁产生概率高和道路拥挤程度不均衡的问题，所以我们在路径选择方面做了车辆的实时调度，具体思路是当车辆在一个路口决定下一次行驶的方向的时候，会计算选择不同道路的剩余距离和该道路的拥挤程度，拥挤程度（road_full）用当前道路上的车辆数目除以道路理论能容纳的最大车辆数目来衡量，0代表道路上没有任何车，1代表道路上塞满了车，然后用road_full来惩罚距离，最终比较Dist×（1+road_full）的大小来实时选择需要的路径，Dist为选择该路口需要行驶的剩余距离。调度器集成在代码中，线上线下总调度时间结果一致。  

### 2.死锁的解除

车辆行驶的时候可能会发生死锁形成环路，我们认为死锁是因为部分道路上车辆数目过多导致的，并且速度慢的车时导致死锁的关键。如果在T时间发生死锁，就找出来发生死锁的车，然后先把发生死锁的车按照车速排序，然后取速度最慢的一半车辆将他们的发车时间推迟到T，对于已经上路的车（除了发生死锁的车），我们不改变他们的发车时间，对于在T时刻还没有上路的车，我们会事先计算他们可能会经过的路段，如果会经过死锁路段，我们也将这些车推迟到T时间以后发车。实验证明通过这样的手段，能很好的解除死锁。  

### 3.发车策略

对于车辆的发车，我们主要考虑到车速，车辆快的车应该具有更大的优先权，因为如果你先发速度慢的，再发速度快的车，肯定没有先发速度快的，再发速度慢的车效果好。在每一个时间片T，我们只发速度最快的车，通过这样的策略我们初赛的分数提高了100分，但是也不能无限制的发车，所以我们去限制道路上最大的车辆数目，只有小于这个数目的时候，才会从车库发车，注意到我们不用担心死锁，因为我们时可以解除死锁的，只是如果你放入更多的车，死锁的概率就会更大，就需要更多的时间去解锁。

### 4.反思

我觉得我们最大的败笔在发车策略上，通过限制路上车的数目来控制发车是不恰当的行为，事实也证明我们过分的拟合了A榜，在数据更换时成绩出现了较大的下滑。这个比赛对我来说已经结束了，祝大家取得好成绩。  

### 代码结构解析
    while(dead_lock == 1): #当发生死锁退出时，应该重新进行一轮调度
        ##初始化一些数据结构
        while(Still_have_cars(Path, Carport_temp, Carport) and dead_lock != 1): #当路上仍然有车的时候并且没有死锁继续调度
            T = T + 1      #时间片+1
            Dispatch_cars(Path, Map, Road, Distance, Cross)  #把所有车辆状态初始化为0，确定车辆的转向
            Look_all_driveway(Path, Road, Map)  #该步骤处理道路内的车
            while(Do_not_process_all_cars(Path)): #当没有处理完所有车，需要循环处理每一个路口
                dead_lock = Look_all_cross(Path, Cross, Map, Road, T) #处理要过马路的车，若发生死锁返回1
                if(dead_lock):
                    print("dead lock happen at " + str(T) + ", " + str(len(have_stated_car)) + " cars have start" + str(count_car(Path)))
                    process_dead_lock(Path, have_stated_car, possible_path, T, Carport_total) #处理死锁，并开始新一轮的调度
                    break
            if(count_car(Path) < 2000):   #路上车数目小于2000，开始放车，先放速度快的车
                Put_car_in_carport(Carport, Carport_temp, T, car_v_record)
                Look_all_carport(Carport, Path, 5000, T, Map, Distance, Road, have_stated_car, car_v_record)
