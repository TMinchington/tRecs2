import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

main_frame = pd.read_csv('/Users/thomas.minchington/Documents/AnzyTrecs/trecs help/trecs help_output_data/trecs2Positions.tsv', sep='\t')

print(main_frame.head())

main_frame['min_cell'] = main_frame.groupby('cell')['time'].transform('min')
main_frame['max_cell'] = main_frame.groupby('cell')['time'].transform('max')

problem_child_ids = ["95838", "95839", "102630", "102631"]



for time in main_frame['time'].unique():
    plot_plot = False
    d_frame = main_frame[(main_frame['min_cell'] == time) & (main_frame['time'] == time)]

    m_frame = main_frame[(main_frame['max_cell'] == time-1) & (main_frame['time'] == time-1)]

    if len(d_frame) == 0 or len(m_frame) == 0:
        continue

    t_frame = pd.concat([d_frame, m_frame])

    t_frame_ids = [str(x) for x in t_frame.cell.values]

    for idx in problem_child_ids:
        for idy in t_frame_ids:
            if idx in idy:
                plot_plot = True

    if plot_plot:
        sns.scatterplot(data=t_frame, x='x', y='y', hue="cell", style="time")
        plt.title(f"Time: {time}, daughers:{len(d_frame)}, mothers:{len(m_frame)}")
        plt.show()
        plt.close()