import simulation as sim
import heapq
import numpy as np


# x, y 격자 크기 정의
x_size, y_size = 40, 24

# 압력 격자 생성. 대류 근사에 사용
inlet_y_range = range(6, 15)
outlet_y_range = range(6, 15)



def heuristic(temp_map):
    return np.max(temp_map)


def greedy_cooler_optimization(initial_configs, max_iterations=20):
    current_coolers = initial_configs
    initial_temp_map = sim.run_simulation(current_coolers)
    current_score = heuristic(initial_temp_map)
    print(f"초기 최고 온도 (T_max): {current_score:.2f} °C\n" + "-"*40)
    moves = [("UP", (-1, 0)), ("DOWN", (1, 0)), ("LEFT", (0, -1)), ("RIGHT", (0, 1))]
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    MAX_ITER = 15  # 반복 횟수
    for step in range(MAX_ITER):
        improved = False
        best_next_configs = None
        
        # 각 쿨러를 하나씩 조작
        for i in range(len(current_coolers)):
            original_pos = current_coolers[i]["pos"]
            original_dir = current_coolers[i]["dir"]
            
            # A. 위치 이동 시도 (상, 하, 좌, 우)
            for _,(dy, dx) in moves:
                ny, nx = original_pos[0] + dy, original_pos[1] + dx
                if 1 <= ny < y_size - 1 and 1 <= nx < x_size - 1:
                    current_coolers[i]["pos"] = (ny, nx)
                    
                    # 시뮬레이션 실행 및 최고 온도(비용) 측정
                    temp_map = sim.run_simulation(current_coolers)
                    score = np.max(temp_map)
                    
                    if score < current_score:
                        current_score = score
                        improved = True
                        best_next_configs = [dict(c) for c in current_coolers]
                    
                    # 원상복구
                    current_coolers[i]["pos"] = original_pos
                    
            # B. 토출 방향 변경 시도 (UP, DOWN, LEFT, RIGHT)
            for ndir in directions:
                if ndir != original_dir:
                    current_coolers[i]["dir"] = ndir
                    
                    temp_map = sim.run_simulation(current_coolers)
                    score = np.max(temp_map)
                    
                    if score < current_score:
                        current_score = score
                        improved = True
                        best_next_configs = [dict(c) for c in current_coolers]
                        
                    current_coolers[i]["dir"] = original_dir

        # 개선된 상태가 있으면 반영하고, 없으면 최적점 도달로 판단하여 종료
        if improved:
            current_coolers = best_next_configs
            print(f"[Iter {step+1}] 온도 개선됨! 현재 최저 T_max: {current_score:.2f} °C")
        else:
            print(f"[Iter {step+1}] 주변에 더 시원해지는 위치가 없습니다. (탐색 완료)")
            break

    print("\n" + "="*40)
    print(f"최적화 최종 완료! 최종 최고 온도: {current_score:.2f} °C")
    print("최적의 쿨러 배치:", current_coolers)
    return current_coolers