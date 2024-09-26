'''
author : kabetani yusei
実行時間294 ms
メモリ93700 KB
'''
import random

class PLACE_TYPE:
    TEMPLE = 0
    RESTAURANT = 1
    SOUVENIR = 2
    STATION = 3

class GENERATE_ROUTE:
    def __init__(self, data):
        self.decision_place = data['decision_place']
        self.limit_time = data['limit_time']
        self.lunch = data['lunch']
        self.now_time = data['now_time']

        # それぞれのタイプで観光地のリストを作成する
        self.temple_list = []
        self.restaurant_list = []
        self.souvenir_list = []
        self.station_list = []
        self.update_place_list(data['place_list'])

        # start地点とgoal地点を追加
        self.start = None
        self.goal = None
        for place in self.station_list:
            if place['id'] == data['start_id']:
                self.start = place
            if place['id'] == data['goal_id']:
                self.goal = place

    def update_place_list(self, place_list):
        for place in place_list:
            place['satisfaction'] += random.choice([-1, 0, 1]) # 満足度を適当にいじって同じルートが選択されることを防ぐ
            if place['type'] == PLACE_TYPE.TEMPLE:
                self.temple_list.append(place)
            elif place['type'] == PLACE_TYPE.RESTAURANT:
                self.restaurant_list.append(place)
            elif place['type'] == PLACE_TYPE.SOUVENIR:
                self.souvenir_list.append(place)
            elif place['type'] == PLACE_TYPE.STATION:
                self.station_list.append(place)

    def _select_restaurant(self):
        return random.choice(self.restaurant_list)

    def _select_souvenir(self):
        return random.choice(self.souvenir_list)

    def _search_best_route(self, dp):
        # ゴール地点の最適解を求める
        best_satisfaction = 0
        best_state = None
        for i in range(2 ** len(dp[0])):
            #2つの条件を満たす必要がある
            #1. 制限時間以内である
            #2. 確定で通りたいやつを通る
            if ((dp[i][-1][0] <= self.limit_time) and
                ((self.decision_place == None) or (i & (2 ** self.decision_place) != 0))):
                if best_state is None:
                    best_satisfaction = dp[i][-1][1]
                    best_state = i
                elif dp[i][-1][1] > dp[best_state][-1][1]:
                    best_satisfaction = dp[i][-1][1]
                    best_state = i
        return best_state

    def generate_route(self):
        # 経路を考えるにあたり、回る候補を求める
        # 飲食店、お土産屋さんは1つずつ選ぶ
        place_candidate_list = [self.start] + self.temple_list
        if self.lunch:
            place_candidate_list.append(self._select_restaurant())
        place_candidate_list.append(self._select_souvenir())
        place_candidate_list.append(self.goal)

        # 以下、bitDPを行う
        cand_list_length = len(place_candidate_list)
        # dpの初期化 tuple(最短時間, おすすめ度の合計)
        dp = [[(100000, 0)] * cand_list_length for _ in range(2 ** cand_list_length)]
        prev = [[-1] * cand_list_length for _ in range(2 ** cand_list_length)]

        # スタート地点の初期値
        dp[0][0] = (0, 0)
        dp[1][0] = (0, 0)
        for i in range(2 ** cand_list_length):
            for j in range(cand_list_length):
                if dp[i][j][0] < 100000:

                    for k in range(1, cand_list_length):
                        if (i // (2 ** k)) % 2 == 0:
                            dist = abs(place_candidate_list[j]['coordinate'][0] - place_candidate_list[k]['coordinate'][0]) + abs(place_candidate_list[j]['coordinate'][1] - place_candidate_list[k]['coordinate'][1])             
                            # 飲食店の場合の計算
                            if place_candidate_list[k]['type'] == PLACE_TYPE.RESTAURANT:
                                calc_time = self.now_time + dp[i][j][0] + dist
                                if 690 <= calc_time <= 780:
                                    satisfaction = place_candidate_list[k]['satisfaction'] 
                                elif 690 <= calc_time <= 840:
                                    satisfaction = place_candidate_list[k]['satisfaction'] // 5
                                elif 660 <= calc_time <= 900:
                                    satisfaction = place_candidate_list[k]['satisfaction'] // 10
                                else:
                                    satisfaction = 0
                            else:
                                satisfaction = place_candidate_list[k]['satisfaction']
                            stay_time = place_candidate_list[k]['stay_time']
                            new_time = dp[i][j][0] + dist + stay_time
                            new_satisfaction = dp[i][j][1] + satisfaction
                            
                            if ((new_satisfaction > dp[i + (2 ** k)][k][1]) or
                                (new_satisfaction == dp[i + (2 ** k)][k][1]) and (new_time < dp[i + (2 ** k)][k][0])):
                                dp[i + (2 ** k)][k] = (new_time, new_satisfaction)
                                prev[i + (2 ** k)][k] = j  # 経路の遷移元を記録

        # 出力
        best_state = self._search_best_route(dp)
        if best_state == None:
            print("条件を満たす経路が見つかりませんでした")
            return False
        total_time = dp[best_state][-1][0]

        # 経路復元
        route = []
        state = best_state
        now = cand_list_length - 1  # ゴール地点

        while now != -1:
            route.append(now)
            next_state = state - (2 ** now)
            now = prev[state][now]
            state = next_state
        route.reverse()
        # 経路の表示
        time_now = self.now_time
        print("経路:")
        for idx in range(len(route)):
            place = place_candidate_list[route[idx]]
            if idx > 0:  # 最初の場所以外は移動時間を計算
                prev_place = place_candidate_list[route[idx - 1]]
                dist = abs(prev_place['coordinate'][0] - place['coordinate'][0]) + abs(prev_place['coordinate'][1] - place['coordinate'][1])
                print(f"移動時間: {dist}分")  # 移動時間を表示
                time_now += dist
            print(f"{time_now // 60:02}:{time_now % 60:02}")  # 時刻と場所を表示
            print(f"ID: {place['id']}, 座標: {place['coordinate']}, 滞在時間: {place['stay_time']}")
            time_now += place['stay_time']

        # 最後に合計移動時間と満足度を表示
        print(f"合計時間: {total_time}分")
        print(f"合計満足度: {dp[best_state][-1][1]}")


if __name__ == "__main__":
    data = {
        'place_list': [
            {'id': 1, 'coordinate': [-20, 16], 'stay_time': 30, 'satisfaction': 10, 'type': 0},
            {'id': 2, 'coordinate': [-3, 15], 'stay_time': 15, 'satisfaction': 10, 'type': 0},
            {'id': 3, 'coordinate': [-19, 7], 'stay_time': 5, 'satisfaction': 10, 'type': 0},
            {'id': 4, 'coordinate': [-6, 7], 'stay_time': 5, 'satisfaction': 10, 'type': 0},
            {'id': 5, 'coordinate': [-14, 1], 'stay_time': 5, 'satisfaction': 10, 'type': 0},
            {'id': 6, 'coordinate': [-9, 3], 'stay_time': 15, 'satisfaction': 10, 'type': 0},
            {'id': 7, 'coordinate': [4, 1], 'stay_time': 5, 'satisfaction': 10, 'type': 0},
            {'id': 8, 'coordinate': [-25, -5], 'stay_time': 5, 'satisfaction': 10, 'type': 0},
            {'id': 9, 'coordinate': [-1, -5], 'stay_time': 5, 'satisfaction': 10, 'type': 0},
            {'id': 10, 'coordinate': [-6, -10], 'stay_time': 5, 'satisfaction': 10, 'type': 0},

            {'id': 11, 'coordinate': [-12, 11], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 12, 'coordinate': [11, 11], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 13, 'coordinate': [23, 7], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 14, 'coordinate': [-19, -10], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 15, 'coordinate': [-8, -5], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 16, 'coordinate': [14, 1], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 17, 'coordinate': [11, -1], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 18, 'coordinate': [14, -1], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 19, 'coordinate': [11, -4], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 20, 'coordinate': [14, -4], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 21, 'coordinate': [11, -7], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 22, 'coordinate': [14, -7], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 23, 'coordinate': [14, -13], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 24, 'coordinate': [21, 0], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 25, 'coordinate': [23, -1], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 26, 'coordinate': [23, -5], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 27, 'coordinate': [21, -7], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 28, 'coordinate': [23, -7], 'stay_time': 40, 'satisfaction': 50, 'type': 1},
            {'id': 29, 'coordinate': [23, -10], 'stay_time': 40, 'satisfaction': 50, 'type': 1},

            {'id': 30, 'coordinate': [1, 7], 'stay_time': 20, 'satisfaction': 3, 'type': 2},
            {'id': 31, 'coordinate': [-19, -5], 'stay_time': 20, 'satisfaction': 3, 'type': 2},
            {'id': 32, 'coordinate': [11, 1], 'stay_time': 20, 'satisfaction': 3, 'type': 2},
            {'id': 33, 'coordinate': [14, -10], 'stay_time': 20, 'satisfaction': 3, 'type': 2},
            {'id': 34, 'coordinate': [21, -10], 'stay_time': 20, 'satisfaction': 3, 'type': 2},

            {'id': 100, 'coordinate': [-27, -6], 'stay_time': 0, 'satisfaction': 0, 'type': 3},
            {'id': 101, 'coordinate': [17, -11], 'stay_time': 0, 'satisfaction': 0, 'type': 3}
        ],
        'start_id': 100,
        'goal_id': 100,
        'decision_place': 1,
        'limit_time': 420,#分単位で管理する(int)
        'lunch': True,
        'now_time': 600#00:00を基準に分で表現(int)
    }
    func = GENERATE_ROUTE(data)
    func.generate_route()