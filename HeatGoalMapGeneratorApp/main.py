import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import io

# ==========================================
# 1. BULLETPROOF DATA LOADER
# ==========================================
with open('events (3).csv', 'r', encoding='utf-8') as f:
    raw_text = f.read()

lines = raw_text.split('\n')
cleaned_lines = []
current_line = ""

for line in lines:
    if not line.strip():
        continue
    if current_line == "":
        current_line = line
    else:
        current_line += line

    if current_line.count(',') >= 8:
        cleaned_lines.append(current_line)
        current_line = ""

df_events = pd.read_csv(io.StringIO('\n'.join(cleaned_lines)))
df_events['X'] = pd.to_numeric(df_events['X'], errors='coerce')
df_events['Y'] = pd.to_numeric(df_events['Y'], errors='coerce')
df_events = df_events.dropna(subset=['X', 'Y'])

goals = df_events[df_events['Event'] == 'Goal'].copy()

# ==========================================
# 2. FIX MISLABELED GOAL & SEPARATE TEAMS
# ==========================================
# Fix the specific Unirea goal at X=64 that was accidentally tagged as 'Opposite'
goals.loc[(goals['Team'] == 'Opposite') & (goals['X'] == 64), 'Team'] = 'Unirea Alba Iulia'

unirea_goals = goals[goals['Team'].str.contains('Unirea', case=False, na=False)].copy()
opp_goals = goals[goals['Team'].str.contains('Opposite', case=False, na=False)].copy()

# ==========================================
# 3. NORMALIZE DIRECTIONS (180 Degree Flip)
# ==========================================
# Normalize Unirea Alba Iulia to the RIGHT side (X > 50)
unirea_left_half = unirea_goals['X'] < 50
unirea_goals.loc[unirea_left_half, 'X'] = 100 - unirea_goals.loc[unirea_left_half, 'X']
unirea_goals.loc[unirea_left_half, 'Y'] = 100 - unirea_goals.loc[unirea_left_half, 'Y']

# Normalize Opposite team to the LEFT side (X < 50)
opp_right_half = opp_goals['X'] > 50
opp_goals.loc[opp_right_half, 'X'] = 100 - opp_goals.loc[opp_right_half, 'X']
opp_goals.loc[opp_right_half, 'Y'] = 100 - opp_goals.loc[opp_right_half, 'Y']

# Define our pitch colors
GRASS_GREEN = '#538053'
LINE_COLOR = '#ffffff'


# ==========================================
# PLOT 1: THE GOAL MAP (Dots Only)
# ==========================================
pitch1 = Pitch(pitch_type='opta', pitch_color=GRASS_GREEN, line_color=LINE_COLOR)
fig1, ax1 = pitch1.draw(figsize=(12, 8))

# Draw the Goal Dots
if not unirea_goals.empty:
    pitch1.scatter(unirea_goals['X'], unirea_goals['Y'], s=150, c='#0044cc',
                   edgecolors='white', linewidth=1.5, ax=ax1, zorder=3, label='Unirea Alba Iulia (Right Net)')

if not opp_goals.empty:
    pitch1.scatter(opp_goals['X'], opp_goals['Y'], s=150, c='#ff0000',
                   edgecolors='white', linewidth=1.5, ax=ax1, zorder=3, label='Opposite Team (Left Net)')

# Labels, Legend, and Scoreboard
ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=12, framealpha=0.9)
ax1.text(50, 95, f'Total Goals: Unirea {len(unirea_goals)} - {len(opp_goals)} Opponent',
         color='white', fontsize=16, va='center', ha='center', zorder=4, fontweight='bold',
         bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', pad=5))
ax1.text(75, 5, 'Unirea Alba Iulia', color='white', fontsize=14, ha='center', va='center', zorder=4, alpha=0.8, fontweight='bold')
ax1.text(25, 5, 'Opposite Team', color='white', fontsize=14, ha='center', va='center', zorder=4, alpha=0.8, fontweight='bold')

plt.title('Match Goal Map', color='black', fontsize=20, fontweight='bold')
plt.show()


# ==========================================
# PLOT 2: PURE HEAT MAP (Two Separate Maps, No Dots)
# ==========================================
pitch2 = Pitch(pitch_type='opta', pitch_color=GRASS_GREEN, line_color=LINE_COLOR, line_zorder=2)
fig2, ax2 = pitch2.draw(figsize=(12, 8))

# Layer 1A: Unirea Heat Map (Right Side)
if not unirea_goals.empty:
    pitch2.kdeplot(
        unirea_goals['X'], unirea_goals['Y'],
        ax=ax2, fill=True, levels=100, thresh=0.05, cmap='YlOrRd', alpha=0.75,
        bw_adjust=0.5
    )

# Layer 1B: Opposite Team Heat Map (Left Side)
if not opp_goals.empty:
    pitch2.kdeplot(
        opp_goals['X'], opp_goals['Y'],
        ax=ax2, fill=True, levels=100, thresh=0.05, cmap='YlOrRd', alpha=0.75,
        bw_adjust=0.5
    )

# Layer 2: Labels and Scoreboard
ax2.text(50, 95, f'Total Goals: Unirea {len(unirea_goals)} - {len(opp_goals)} Opponent',
         color='white', fontsize=16, va='center', ha='center', zorder=4, fontweight='bold',
         bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', pad=5))
ax2.text(75, 5, 'Unirea Alba Iulia', color='white', fontsize=14, ha='center', va='center', zorder=4, alpha=0.8, fontweight='bold')
ax2.text(25, 5, 'Opposite Team', color='white', fontsize=14, ha='center', va='center', zorder=4, alpha=0.8, fontweight='bold')

plt.title('Match Goal Heat Map', color='black', fontsize=20, fontweight='bold')
plt.show()