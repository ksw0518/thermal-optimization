import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# 각 격자별 상태 정의
EMPTY = 0
WALL = 1
SERVER = 2
FAN = 3
INLET = 4
OUTLET = 5

# x, y 격자 크기 정의
x_size, y_size = 40, 24

# 압력 격자 생성. 대류 근사에 사용
inlet_y_range = range(6, 15)
outlet_y_range = range(6, 15)


MAX_STEP = 500
ALPHA = 0.05        # 열확산 계수
ROOM_TEMP = 25.0    # 실내 기본 온도
SERVER_HEAT = 4.0   # 서버 발열량


server_racks = [(10, 12), (10, 15), (18, 12), (18, 15)]  # (y, x) 좌표계 기준 서버 위치

# 시뮬레이션

cooler_configs = [
    {"pos": (13, 13), "dir": "RIGHT"},
    {"pos": (13, 20), "dir": "RIGHT"}
]

def simulate_pressure():
    pressure = np.zeros((y_size, x_size))
    pressure[inlet_y_range, 5] = 10.0   # 고압부 (입구)
    pressure[outlet_y_range, 20] = 0.0  # 저압부 (출구)
    inlet_coords = [(y, 5) for y in inlet_y_range]
    outlet_coords = [(y, 20) for y in outlet_y_range]
    
    for i in range(100):
        for y in range(1, y_size - 1):
            for x in range(1, x_size - 1):
                pressure[y, x] = (
                    pressure[y, x - 1]
                    + pressure[y, x + 1]
                    + pressure[y - 1, x]
                    + pressure[y + 1, x]
                ) / 4

        # 위아래 벽: 수직 방향 압력 변화 없음
        pressure[0, :] = pressure[1, :]
        pressure[-1, :] = pressure[-2, :]

        # 경계 압력 유지
        pressure[6:15, 5] = 10
        pressure[6:15, 20] = 0
    return pressure


def simulate_heat(pressure, cooler_settings):
    # plt.ion()

    



    dy_pressure, dx_pressure = np.gradient(pressure)


    temperature = np.full((y_size, x_size), ROOM_TEMP)

    # fig, ax = plt.subplots(figsize=(12, 7))

    # im = ax.imshow(
    #     temperature,
    #     cmap="hot",
    #     origin="upper",
    #     interpolation="nearest",
    #     vmin=25,
    #     vmax=45
    # )

    #fig.colorbar(im, ax=ax, label="Temperature (°C)")
    for step in range(MAX_STEP):
        next_temp = temperature.copy()
        
        for y in range(1, y_size - 1):
            for x in range(1, x_size - 1):
                # A. 열전도 (Diffusion - 주변 4방향 온도 확산)
                neighbor_sum = (
                    temperature[y, x - 1] +
                    temperature[y, x + 1] +
                    temperature[y - 1, x] +
                    temperature[y + 1, x]
                )
                diffusion = ALPHA * (neighbor_sum - 4 * temperature[y, x])
                
                # B. 압력 기반 대류 (Advection - 압력 구배에 따른 바람 방향으로 열 이동)
                # 압력이 높은 곳에서 낮은 곳으로 공기가 이동하며 온도를 운반합니다.
                vx = dx_pressure[y, x]
                vy = dy_pressure[y, x]


                for cooler in cooler_settings:
                    cy, cx = cooler["pos"]
                    direction = cooler["dir"]
                    
                    # 쿨러 위치 및 토출 방향에 따른 범위 판정 (팬 전방 3칸 내외)
                    if direction == "RIGHT" and cy == y and 0 <= (x - cx) <= 3:
                        vx += 3.0
                    elif direction == "LEFT" and cy == y and -3 <= (x - cx) <= 0:
                        vx -= 3.0
                    elif direction == "DOWN" and cx == x and 0 <= (y - cy) <= 3:
                        vy += 3.0
                    elif direction == "UP" and cx == x and -3 <= (y - cy) <= 0:
                        vy -= 3.0
                # 3. 업윈드(Upwind) 방식을 이용한 대류(Advection) 계산
                advection_x = (
                    -vx * (temperature[y, x] - temperature[y, x - 1]) if vx > 0 
                    else -vx * (temperature[y, x + 1] - temperature[y, x])
                )
                advection_y = (
                    -vy * (temperature[y, x] - temperature[y - 1, x]) if vy > 0 
                    else -vy * (temperature[y + 1, x] - temperature[y, x])  # 오타 수정 완료
                )
                
                # 4. 최종 온도 업데이트 (전도 + 대류 반영)
                next_temp[y, x] = temperature[y, x] + diffusion + 0.1 * (advection_x + advection_y)

        # C. 서버 랙 발열 (Source Term)
        for r_y, r_x in server_racks:
            next_temp[r_y, r_x] += SERVER_HEAT
            
        # D. 압력 소스/싱크 영역 온도 조절 (쿨러 효과)
        next_temp[6:15, 5] = ROOM_TEMP  # 찬 공기 유입구

        temperature = next_temp.copy()
        # 반복문 내부, temperature 업데이트 이후에 추가
        # if step % 10 == 0:
        #     im.set_data(temperature)

        #     ax.set_title(
        #         f"Temperature Distribution - Step {step}"
        #     )

        #     fig.canvas.draw_idle()
        #     plt.pause(0.01)
        # # E. 실시간 시각화 (일정 주기마다 출력)
        # if step % 10 == 0:
        #     for r_y, r_x in server_racks:
        #         ax.scatter(r_x, r_y, c='cyan', marker='s', s=80, label='Server')
        #     for cooler in cooler_configs:
        #         cy, cx = cooler["pos"]
        #         ax.scatter(cx, cy, c='lime', marker='^', s=100)
        #     for y_in, x_in in inlet_coords:
        #         ax.scatter(x_in, y_in, c='blue', marker='o', s=50, label='Inlet')
        #     for y_out, x_out in outlet_coords:
        #         ax.scatter(x_out, y_out, c='magenta', marker='x', s=50, label='Outlet')
        #     im.set_data(temperature)
        #     ax.set_title(f'Data Center Temperature Simulation - Step {step}')
        #     plt.draw()
        #     plt.pause(0.001)
    return temperature

def run_simulation(cooler_settings):
    
    pressure_map = simulate_pressure()
    temperature_map = simulate_heat(pressure_map, cooler_settings)
    return temperature_map



# final_temperature = run_simulation(cooler_configs)
# max_temp = np.max(final_temperature)
# print(f"시뮬레이션 완료! 최종 핫스팟 최고 온도 (T_max): {max_temp:.2f} °C")

# # Matplotlib 시각화 설정
# fig, ax = plt.subplots(figsize=(10, 6))
# im = ax.imshow(final_temperature, cmap='hot', interpolation='nearest', origin='upper', vmin=25, vmax=45)
# cbar = plt.colorbar(im, ax=ax, label='Temperature (°C)')
# ax.set_xlabel('X Grid')
# ax.set_ylabel('Y Grid')
# ax.set_title(f'Data Center Final Temperature Distribution (Max T: {max_temp:.2f}°C)')

# # 마커 표시 (서버, 쿨러, 입구, 출구)
# for r_y, r_x in server_racks:
#     ax.scatter(r_x, r_y, c='cyan', marker='s', s=80, label='Server' if r_y == server_racks[0][0] else "")
# for cooler in cooler_configs:
#     cy, cx = cooler["pos"]
#     ax.scatter(cx, cy, c='lime', marker='^', s=100, label='Cooler' if cooler == cooler_configs[0] else "")
# for y_in in inlet_y_range:
#     ax.scatter(5, y_in, c='blue', marker='o', s=25, label='Inlet' if y_in == inlet_y_range[0] else "")
# for y_out in outlet_y_range:
#     ax.scatter(20, y_out, c='magenta', marker='x', s=25, label='Outlet' if y_out == outlet_y_range[0] else "")

# ax.legend(loc='upper right')
# plt.show()
    