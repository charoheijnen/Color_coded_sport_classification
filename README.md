# Color_coded_sport_classification
import pandas as pd
import matplotlib.pyplot as plt

# colors based on mitchell classification
# blue = dynamic, red = static, green = both high, gray = both low
sport_color = {
    "Rowing": "green",
    "Track": "blue",
    "Cycling": "green",
    "Soccer": "blue",
    "Canoeing": "green",
    "Roller-skating": "green",
    "Swimming": "blue",
    "Volleyball": "blue",
    "Pentathlon": "blue",
    "Tennis": "blue",
    "Fencing": "gray",
    "Alpine skiing": "green",
    "Cross-country skiing": "green",
    "Equestrianism": "red",
    "Team handball": "blue",
    "Yachting": "red",
    "Roller hockey": "blue",
    "Water polo": "blue",
    "Tae kwon do": "blue",
    "Wrestling and judo": "red",
    "Bobsledding": "green",
    "Boxing": "blue",
    "Diving": "red",
    "Field weight events": "red",
    "Weightlifting": "red",
}

sports = ["Rowing","Track","Cycling","Soccer","Canoeing","Roller-skating",
    "Swimming","Volleyball","Pentathlon","Tennis","Fencing","Alpine skiing",
    "Cross-country skiing","Equestrianism","Team handball","Yachting",
    "Roller hockey","Water polo","Tae kwon do","Wrestling and judo",
    "Bobsledding","Boxing","Diving","Field weight events","Weightlifting"]

lved_mean = [56.0,51.4,54.8,54.9,54.5,49.0,53.0,53.7,52.4,50.0,51.7,52.0,
    54.5,50.4,51.8,51.2,53.4,54.7,50.6,52.6,55.1,52.5,49.6,55.5,53.2]

lved_sd = [3,4,5,4,3,4,4,3,4,3,5,3,4,3,4,4,3,3,4,5,2,3,3,4,3]

wt_mean = [11.3,9.8,10.4,9.9,10.5,9.0,9.3,9.4,9.2,9.1,9.2,8.9,9.6,9.0,
    8.5,9.0,9.7,10.7,8.7,10.2,9.6,9.8,8.7,10.0,10.4]

wt_sd = [1.3,1.2,1.1,0.7,1.5,1.0,1.2,1.0,0.9,1.0,1.3,0.9,0.8,0.8,0.9,0.8,
    0.9,0.6,1.2,0.9,0.5,1.0,1.1,0.5,0.7]

# shorten some labels so they don't overlap on the plot
abbrev = {
    "Cross-country skiing": "XC Ski",
    "Wrestling and judo": "Wrest/Judo",
    "Field weight events": "Throws",
    "Roller-skating": "Roller",
    "Team handball": "Handball",
    "Water polo": "WaterPolo",
    "Alpine skiing": "Alpine",
    "Tae kwon do": "TKD",
    "Roller hockey": "R.Hockey",
    "Equestrianism": "Equestrian",
}

df = pd.DataFrame({
    "Sport": sports,
    "LVED_mean": lved_mean,
    "LVED_sd": lved_sd,
    "WallThickness_mean": wt_mean,
    "WallThickness_sd": wt_sd,
})
df["color"] = df["Sport"].map(sport_color)
df["label"] = df["Sport"].apply(lambda s: abbrev.get(s, s))

plt.figure(figsize=(11, 8))

for i, row in df.iterrows():
    plt.errorbar(row["LVED_mean"], row["WallThickness_mean"],
        xerr=row["LVED_sd"], yerr=row["WallThickness_sd"],
        fmt='o', capsize=2, elinewidth=0.6, markersize=6,
        color=row["color"], ecolor=row["color"], alpha=0.8)
    plt.annotate(row["label"], (row["LVED_mean"], row["WallThickness_mean"]),
        xytext=(5,5), textcoords="offset points", fontsize=7.5, color=row["color"])

# legend 
blue_dot = plt.Line2D([0],[0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='High Dynamic')
red_dot = plt.Line2D([0],[0], marker='o', color='w', markerfacecolor='red', markersize=8, label='High Static')
green_dot = plt.Line2D([0],[0], marker='o', color='w', markerfacecolor='green', markersize=8, label='High Dynamic + Static')
gray_dot = plt.Line2D([0],[0], marker='o', color='w', markerfacecolor='gray', markersize=8, label='Low Both')

plt.xlabel("LVED (mm)")
plt.ylabel("Wall Thickness (mm)")
plt.title("Athlete Cardiac Remodeling by Sport\n(Colour = Mitchell Classification)")
plt.legend(handles=[blue_dot, red_dot, green_dot, gray_dot], fontsize=9, loc="upper left")
plt.grid(True)
plt.tight_layout()
plt.show()
