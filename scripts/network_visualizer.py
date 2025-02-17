import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # This import registers the 3D projection
import psutil
import time
from matplotlib.gridspec import GridSpec
from collections import Counter

def visualize_network(filter_status=None, update_interval=1, max_updates=100):
    """
    Visualizes network connections in 3D with live updates and includes a pie chart of connection statuses.
    
    Args:
      filter_status: Optional filter to show only certain connection statuses (e.g., 'LISTEN', 'ESTABLISHED').
      update_interval: Time in seconds between updates.
      max_updates: Maximum number of updates before stopping.
    """
    # Create figure with GridSpec: 2 columns, one for the 3D plot, one for the pie chart.
    fig = plt.figure(figsize=(12, 6))
    gs = GridSpec(1, 2, width_ratios=[2, 1])
    ax3d = fig.add_subplot(gs[0], projection='3d')
    ax_pie = fig.add_subplot(gs[1])
    
    update_count = 0

    while update_count < max_updates:
        # Check if the figure window still exists.
        if not plt.fignum_exists(fig.number):
            print("Figure closed by user.")
            break
        
        # Retrieve current network connections
        connections = psutil.net_connections(kind='inet')
        x_vals, y_vals, z_vals, colors = [], [], [], []
        labels = []
        status_list = []
        
        for i, conn in enumerate(connections):
            if filter_status and conn.status != filter_status:
                continue

            # x: connection index, y: local port, z: remote port (or 0)
            x_vals.append(i)
            y_vals.append(conn.laddr.port)
            z_vals.append(conn.raddr.port if conn.raddr else 0)
            status_list.append(conn.status)
            
            # Set color based on connection status.
            if conn.status == 'LISTEN':
                colors.append('r')
            elif conn.status == 'ESTABLISHED':
                colors.append('g')
            elif conn.status == 'TIME_WAIT':
                colors.append('b')
            else:
                colors.append('y')
            
            labels.append(f"{conn.laddr.ip}:{conn.laddr.port}\n→ {conn.raddr.ip if conn.raddr else 'N/A'}:"
                          f"{conn.raddr.port if conn.raddr else 'N/A'}")
        
        # Clear previous plots
        ax3d.cla()
        ax_pie.cla()
        
        # 3D Scatter plot for network connections.
        ax3d.scatter(x_vals, y_vals, z_vals, c=colors, s=50)
        ax3d.set_xlabel('Connection Number')
        ax3d.set_ylabel('Local Port')
        ax3d.set_zlabel('Remote Port')
        ax3d.set_title("3D Network Activity")
        
        # Add annotations for each connection (optional; may be cluttered if too many).
        for xi, yi, zi, lab, col in zip(x_vals, y_vals, z_vals, labels, colors):
            ax3d.text(xi, yi, zi, lab, fontsize=7, color=col)
        
        # Create a status summary text and place it above the 3D plot.
        counts = Counter(status_list)
        total = len(status_list)
        summary_text = f"Total: {total}\n" + "\n".join([f"{status}: {count}" for status, count in counts.items()])
        ax3d.text2D(0.05, 0.95, summary_text, transform=ax3d.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        
        # Pie chart for the breakdown of connection statuses.
        if counts:
            statuses = list(counts.keys())
            count_values = list(counts.values())
            # Define colors matching our scatter plot
            status_color_map = {
                'LISTEN': 'r',
                'ESTABLISHED': 'g',
                'TIME_WAIT': 'b'
            }
            pie_colors = [status_color_map.get(s, 'y') for s in statuses]
            ax_pie.pie(count_values, labels=statuses, autopct='%1.1f%%', startangle=90, colors=pie_colors)
            ax_pie.set_title("Connection Status Breakdown")
        else:
            ax_pie.text(0.5, 0.5, "No Data", ha='center', va='center')
        
        # Draw and pause for update interval.
        plt.draw()
        plt.pause(update_interval)
        update_count += 1

    # Close figure if it still exists.
    if plt.fignum_exists(fig.number):
        plt.close(fig)

if __name__ == "__main__":
    visualize_network(filter_status=None, update_interval=2, max_updates=50)
