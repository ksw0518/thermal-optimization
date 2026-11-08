import search
import simulation as sim
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation, PillowWriter

def visualize_environment(cooler_configs):

    fig, ax = plt.subplots(figsize=(13, 7))

    # 1. 전체 공간
    ax.set_xlim(-0.5, sim.x_size - 0.5)
    ax.set_ylim(sim.y_size - 0.5, -0.5)

    ax.set_xticks(range(sim.x_size))
    ax.set_yticks(range(sim.y_size))

    ax.grid(True, color="lightgray", linewidth=0.5)

    # 2. 공기 입구
    for y in sim.inlet_y_range:
        ax.add_patch(
            Rectangle(
                (5 - 0.5, y - 0.5),
                1, 1,
                facecolor="deepskyblue",
                edgecolor="white"
            )
        )

    # 3. 공기 출구
    for y in sim.outlet_y_range:
        ax.add_patch(
            Rectangle(
                (20 - 0.5, y - 0.5),
                1, 1,
                facecolor="magenta",
                edgecolor="white"
            )
        )

    # 4. 서버 랙
    for y, x in sim.server_racks:
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1, 1,
                facecolor="cyan",
                edgecolor="black",
                linewidth=1.5
            )
        )

    # 5. 냉각기 및 토출 방향
    direction_vectors = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0)
    }

    for cooler in cooler_configs:

        cy, cx = cooler["pos"]
        direction = cooler["dir"]

        # 냉각기 위치
        ax.scatter(
            cx, cy,
            color="limegreen",
            marker="s",
            s=180,
            edgecolors="black",
            zorder=5
        )

        # 토출 방향 화살표
        dx, dy = direction_vectors[direction]

        ax.annotate(
            "",
            xy=(cx + dx * 2, cy + dy * 2),
            xytext=(cx, cy),
            arrowprops=dict(
                arrowstyle="->",
                color="green",
                linewidth=2.5
            )
        )
    ax.set_xlabel("X Grid")
    ax.set_ylabel("Y Grid")

    ax.set_aspect("equal")
    plt.tight_layout()
    plt.show()


def find_best():
    # --- 1. 무작위 초기 쿨러 설정 생성 (개수: 2개) ---
    num_coolers = 2
    current_coolers = []
    possible_directions = ["UP", "DOWN", "LEFT", "RIGHT"]

    while len(current_coolers) < num_coolers:
        rand_y = np.random.randint(6, 22)
        rand_x = np.random.randint(8, 25)
        
        # 서버 랙 위치나 입구/출구 경계와 겹치지 않도록 필터링
        is_server = (rand_y, rand_x) in sim.server_racks
        is_inlet = (rand_x == 5 and rand_y in sim.inlet_y_range)
        is_outlet = (rand_x == 20 and rand_y in sim.outlet_y_range)
        
        if not (is_server or is_inlet or is_outlet):
            rand_dir = np.random.choice(possible_directions)
            current_coolers.append({"pos": (rand_y, rand_x), "dir": rand_dir})

    print("초기 무작위 쿨러 배치:", current_coolers)




    best_config = search.greedy_cooler_optimization(current_coolers)

    best_temp_map = sim.run_simulation(best_config)
    final_temperature = np.max(best_temp_map)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(best_temp_map, cmap='hot', interpolation='nearest', origin='upper', vmin=25, vmax=45)
    cbar = plt.colorbar(im, ax=ax, label='Temperature (°C)')
    ax.set_xlabel('X Grid')
    ax.set_ylabel('Y Grid')
    ax.set_title(f'Optimized Cooling Final Result (Max T: {final_temperature:.2f}°C)')

    # 마커 표시 (서버, 쿨러, 입구, 출구)
    for r_y, r_x in sim.server_racks:
        ax.scatter(r_x, r_y, c='cyan', marker='s', s=80, label='Server' if r_y == sim.server_racks[0][0] else "")
    for cooler in best_config:
        cy, cx = cooler["pos"]
        ax.scatter(cx, cy, c='lime', marker='^', s=100, label='Optimized Cooler' if cooler == best_config[0] else "")
    for y_in in sim.inlet_y_range:
        ax.scatter(5, y_in, c='blue', marker='o', s=25, label='Inlet' if y_in == sim.inlet_y_range[0] else "")
    for y_out in sim.outlet_y_range:
        ax.scatter(20, y_out, c='magenta', marker='x', s=25, label='Outlet' if y_out == sim.outlet_y_range[0] else "")

    ax.legend(loc='upper right')
    plt.show(block=True)


# visualize_environment(cooler_configs = [
#     {"pos": (21, 15), "dir": "UP"},
#     {"pos": (10, 18), "dir": "LEFT"}
# ])

find_best()