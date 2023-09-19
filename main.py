from matplotlib import colors as mcolors
import tkinter as tk
from tkinter import colorchooser
from tkinter import font
from PIL import Image, ImageTk
from itertools import cycle
import time
import os
import sys

# Initialize variables for score tracking
teams = ["Gap2Gap", "Away"]
teams_short = ["G2G", "AWY"]
inning_halfs = ['Top', 'Mid', 'Bot', 'End']
current_half = 0
inning = 1
strikes = 0
balls = 0
outs = 0

home_score = 0
home_hits = 0
home_errors = 0
home_inning_runs = [0]

away_score = 0
away_hits = 0
away_errors = 0
away_inning_runs =[0]
failed = False
final = False
pitch_count = [0,0]
current_pitch_count = 0

bases = [False, False, False]
show_pitch_count = False

home_team_color = mcolors.CSS4_COLORS["lightblue"] 
home_team_color2 = mcolors.CSS4_COLORS["black"]
# home_team_color2 = mcolors.XKCD_COLORS["xkcd:pink"] 
away_team_color= mcolors.XKCD_COLORS["xkcd:crimson"]
away_team_color2= mcolors.CSS4_COLORS["ivory"]

base_path = os.getcwd()
resource_folder = os.path.join(base_path, 'resources')

name_tooltip_window = None

def increment_inning():
    global inning
    global current_half
    global outs
    global pitch_count
    global current_pitch_count
    
    if current_half < len(inning_halfs)-1:
        current_half += 1
        if outs == 3:
            outs = 0
        if current_half == 3:
            print("End of Inning")
            pitch_count[0] = current_pitch_count
            current_pitch_count = pitch_count[1]
            clear_bases()
            reset_count()
            outs = 0
            try:
                home_inning_runs[inning]
            except:
                home_inning_runs.append(0)
        elif current_half==1:
            print("Middle of Inning")
            pitch_count[1] = current_pitch_count
            current_pitch_count = pitch_count[0]
            clear_bases()
            reset_count()
            outs = 0
            try:
                away_inning_runs[inning]
            except:
                away_inning_runs.append(0)
    else:
        inning += 1
        current_half = 0
        if outs==3:
            outs=0
        
    update_score()

def decrement_inning():
    global inning
    global current_half
    
    if current_half == 0 and inning > 1:
        inning -= 1
        current_half = len(inning_halfs)-1
        
    elif current_half == 0:
        current_half = 0
    else:
        current_half -= 1 
    update_score()

def increment_home_score():
    global home_score, home_inning_runs, failed
    home_score += 1
    try:
        home_inning_runs[inning-1] += 1
    except:
        failed = True
    update_score()

def decrement_home_score():
    global home_score, home_inning_runs
    if home_score > 0:
        home_score -= 1
        home_inning_runs[inning-1] -= 1
    update_score()

def increment_away_score():
    global away_score, away_inning_runs, failed
    away_score += 1
    try:
        away_inning_runs[inning-1] += 1
    except:
        failed = True
    update_score()

def decrement_away_score():
    global away_score, away_inning_runs
    if away_score > 0:
        away_score -= 1
        away_inning_runs[inning-1] -= 1
    update_score()
      
def increment_strikes():
    global strikes
    global current_pitch_count
    
    if current_half == 0 or current_half == 2:
        current_pitch_count += 1
        if strikes < 2:
            strikes += 1
        else:
            strikes = 0
            increment_outs()
            reset_count()
    update_score()

def decrement_strikes():
    global strikes
    global current_pitch_count
    
    if current_half == 0 or current_half == 2:
        if strikes > 0 and current_pitch_count >0:
            current_pitch_count -=1
            strikes -= 1
    update_score()

def increment_balls():
    global balls
    global current_pitch_count
    
    if current_half == 0 or current_half == 2:
        current_pitch_count +=1
        if balls < 3:
            balls += 1
        else:
            force_advance_runner()
            balls = 0
            reset_count()
    update_score()

def decrement_balls():
    global balls
    global current_pitch_count
    
    if current_half == 0 or current_half == 2:
        if balls > 0 and current_pitch_count >0:
            current_pitch_count -=1
            balls -= 1
    update_score()
    
def increment_hits():
    global home_hits, away_hits
    if current_half == 0:
        away_hits += 1
    elif current_half == 2:
        home_hits += 1
    update_score()

def decrement_hits():
    global home_hits, away_hits
    if current_half == 0 and away_hits > 0:
        away_hits -= 1
    elif current_half == 2 and home_hits > 0:
        home_hits -=1
    update_score()
    
def increment_errors():
    global home_errors, away_errors
    if current_half == 0:
        home_errors += 1
    elif current_half == 2:
        away_errors += 1
    update_score()

def decrement_errors():
    global home_errors, away_errors
    if current_half == 0 and home_errors > 0:
        home_errors -= 1
    elif current_half == 2 and away_errors > 0:
        away_errors -=1
    update_score()
    
def increment_outs():
    global outs
    global current_half
    if current_half == 0 or current_half == 2:
        if outs < 2:
            outs += 1
        else:
            increment_inning()
            # current_half += 1
            outs = 3
            
    update_score()

def decrement_outs():
    global outs
    if current_half == 0 or current_half == 2:
        if outs > 0:
            outs -= 1
    update_score()
    
def force_advance_runner():
    global bases
    if bases[0] and bases[1] and bases[2]:
        score_run()
    elif bases[0] and bases[1]:
        bases[2] = True
    elif bases[0]:
        bases[1] = True
    else:
        bases[0] = True
    update_score()
        
def clear_bases():
    global bases 
    bases = [False, False, False]
    update_score()

def score_run():
    if current_half == 0:
        increment_away_score()
    if current_half == 2:
        increment_home_score()
    update_score()
    
def reset_count():
    global balls
    global strikes
    balls = 0
    strikes = 0
    update_score()
    
def new_game():
    global teams, teams_short, current_half, inning, strikes, balls, outs, home_score, home_hits, home_errors, home_inning_runs, away_score, away_hits, away_errors, away_inning_runs, bases, pitch_count, current_pitch_count
    teams = ["Home", "Away"]
    teams_short = ["HME", "AWY"]
    current_half = 0
    inning = 1
    strikes = 0
    balls = 0
    outs = 0

    home_score = 0
    home_hits = 0
    home_errors = 0
    home_inning_runs = [0]
    away_score = 0
    away_hits = 0
    away_errors = 0
    away_inning_runs = [0]

    bases = [False, False, False]
    
    pitch_count = [0,0]
    current_pitch_count = 0
    update_score()
    
def new_pitcher():
    global current_pitch_count
    current_pitch_count = 0
    update_score()

def toggle_pitch_count():
    global show_pitch_count
    show_pitch_count = not show_pitch_count

def team_config():
    config_window = tk.Toplevel(root)
    config_window.title("Team Configuration")
    
    def config_save():
        global teams, home_team_color, away_team_color, home_team_color2, away_team_color2
        name_checker()
        teams[0] = home_name_entry.get()
        teams[1] = away_name_entry.get()
        teams_short[0] = home_short_name_entry.get()
        teams_short[1] = away_short_name_entry.get()
        home_team_color = home_team_color_swatch.itemcget(home_team_color_swatch_rectangle, "fill")
        away_team_color = away_team_color_swatch.itemcget(away_team_color_swatch_rectangle, "fill")
        home_team_color2 = home_team_color_swatch2.itemcget(home_team_color_swatch_rectangle2, "fill")
        away_team_color2 = away_team_color_swatch2.itemcget(away_team_color_swatch_rectangle2, "fill")
        config_window.destroy()
        update_score()
        
    def switch_teams():
        name_checker()
        dummy_name = home_name_entry.get()
        home_name_entry.delete(0, tk.END)
        dummy_short = home_short_name_entry.get()
        home_short_name_entry.delete(0, tk.END)
        dummy_color = home_team_color_swatch.itemcget(home_team_color_swatch_rectangle, "fill")
        dummy_color2 = home_team_color_swatch2.itemcget(home_team_color_swatch_rectangle2, "fill")
        
        home_name_entry.insert(0, away_name_entry.get())
        away_name_entry.delete(0, tk.END)
        home_short_name_entry.insert(0, away_short_name_entry.get())
        away_short_name_entry.delete(0, tk.END)
        home_team_color = home_team_color_swatch.itemconfig(home_team_color_swatch_rectangle, fill=away_team_color_swatch.itemcget(away_team_color_swatch_rectangle, "fill"))
        home_team_color2 = home_team_color_swatch2.itemconfig(home_team_color_swatch_rectangle2, fill=away_team_color_swatch2.itemcget(away_team_color_swatch_rectangle2, "fill"))
                                                      
        away_name_entry.insert(0, dummy_name)
        away_short_name_entry.insert(0, dummy_short)
        away_team_color = away_team_color_swatch.itemconfig(away_team_color_swatch_rectangle, fill=dummy_color)
        away_team_color2 = away_team_color_swatch2.itemconfig(away_team_color_swatch_rectangle2, fill=dummy_color2)

    def name_checker():
        def shortener(name, length):
            vowels = "AEIOU"
            if len(name) > length:
                for i in range(len(name) - 2, -1, -1):
                    if name[i] in vowels and name[i - 1] not in vowels:
                        name = name[:i] + name[i+1:]
                if len(name) > length:
                    temp = name[:(length-1)]
                    name = temp + name[length]
            return name
        max_long = 9
        max_short = 3
        
        home_name = home_name_entry.get().upper()
        away_name = away_name_entry.get().upper()
        
        home_short = home_short_name_entry.get().upper()
        away_short = away_short_name_entry.get().upper()
        
        home_name = shortener(home_name, max_long)
        away_name = shortener(away_name, max_long)
        home_short = shortener(home_short, max_short)
        away_short = shortener(away_short, max_short)
        
        home_name_entry.delete(0, tk.END)
        home_short_name_entry.delete(0, tk.END)
        away_name_entry.delete(0, tk.END)
        away_short_name_entry.delete(0, tk.END)
        
        home_name_entry.insert(0, home_name)
        away_name_entry.insert(0, away_name)
        home_short_name_entry.insert(0, home_short)
        away_short_name_entry.insert(0, away_short)
        
        
    # def show_name_tooltip(event):
    #     global name_tooltip_window
    #     tooltip_text = "Truncate names longer than 9 characters"
    #     x, y, _, _ = config_window.bbox("insert")
    #     x += config_window.winfo_rootx() + 25
    #     y += config_window.winfo_rooty() + 30
    
    #     name_tooltip_window = tk.Toplevel(config_window)
    #     name_tooltip_window.wm_overrideredirect(True)
    #     name_tooltip_window.wm_geometry(f"+{x}+{y}")
    
    #     tooltip_label = tk.Label(name_tooltip_window, text=tooltip_text, background="lightyellow", relief="solid", borderwidth=1)
    #     tooltip_label.pack()
   
    # def hide_name_tooltip(event):
    #     global name_tooltip_window
    #     name_tooltip_window.destroy()
    #     name_tooltip_window = None
       
    section_font = font.Font(size=12, weight='bold')
    home_label = tk.Label(config_window, text="Home Team Settings", font=section_font)
    home_label.grid(row=0, column=0, columnspan=3, sticky='w')
    home_name_label = tk.Label(config_window, text="Team Name: ")
    home_name_label.grid(row=1, column=1)
    home_name_entry = tk.Entry(config_window)
    home_name_entry.insert(0, teams[0])
    home_name_entry.grid(row=1, column=2)
    home_short_name_label = tk.Label(config_window, text="Abbreviated: ")
    home_short_name_label.grid(row=2, column=1)
    home_short_name_entry = tk.Entry(config_window)
    home_short_name_entry.insert(0, teams_short[0])
    home_short_name_entry.grid(row=2, column=2)
    home_team_color_swatch = tk.Canvas(config_window, width=50, height=35)
    home_team_color_swatch.grid(row=1, column=5)
    home_team_color_swatch_rectangle = home_team_color_swatch.create_rectangle(10, 10, 40, 30, fill=home_team_color)
    home_team_color_swatch.tag_bind(home_team_color_swatch_rectangle, "<Button-1>", open_color_picker)
    home_team_color_swatch2 = tk.Canvas(config_window, width=50, height=35)
    home_team_color_swatch2.grid(row=2, column=5)
    home_team_color_swatch_rectangle2 = home_team_color_swatch2.create_rectangle(10, 10, 40, 30, fill=home_team_color2)
    home_team_color_swatch2.tag_bind(home_team_color_swatch_rectangle2, "<Button-1>", open_color_picker)
    
    away_label = tk.Label(config_window, text="Away Team Settings", font=section_font)
    away_label.grid(row=4, column=0, columnspan=3, sticky='w')
    away_name_label = tk.Label(config_window, text="Team Name: ")
    away_name_label.grid(row=5, column=1)
    away_name_entry = tk.Entry(config_window)
    away_name_entry.insert(0, teams[1])
    away_name_entry.grid(row=5, column=2)
    away_short_name_label = tk.Label(config_window, text="Abbreviated: ")
    away_short_name_label.grid(row=6, column=1)
    away_short_name_entry = tk.Entry(config_window)
    away_short_name_entry.insert(0, teams_short[1])
    away_short_name_entry.grid(row=6, column=2)
    away_team_color_swatch = tk.Canvas(config_window, width=50, height=35)
    away_team_color_swatch.grid(row=5, column=5)
    away_team_color_swatch_rectangle = away_team_color_swatch.create_rectangle(10, 10, 40, 30, fill=away_team_color)
    away_team_color_swatch.tag_bind(away_team_color_swatch_rectangle, "<Button-1>", open_color_picker)
    away_team_color_swatch2 = tk.Canvas(config_window, width=50, height=35)
    away_team_color_swatch2.grid(row=6, column=5)
    away_team_color_swatch_rectangle2 = away_team_color_swatch2.create_rectangle(10, 10, 40, 30, fill=away_team_color2)
    away_team_color_swatch2.tag_bind(away_team_color_swatch_rectangle2, "<Button-1>", open_color_picker)
    
    
    # note_font = font.Font(size = 10, slant= 'italic')
    # note_config_label = tk.Label(config_window, text="Truncate names longer than 9 characters", font=note_font)
    # note_config_label.grid(row=, column=1, columnspan=4)
    
    config_spacer_label = tk.Label(config_window, text="     ")
    config_spacer_label.grid(row=0, column=3)
    
    save_button = tk.Button(config_window, text="Switch Home/Away", command=switch_teams)
    save_button.grid(row=7, column=0, columnspan=2)
    
    save_button = tk.Button(config_window, text="Save Changes", command=config_save)
    save_button.grid(row=7, column=2, columnspan=2)
    
    # home_name_entry.bind("<Enter>", show_name_tooltip)
    # home_name_entry.bind("<Leave>", hide_name_tooltip)
    # away_name_entry.bind("<Enter>", show_name_tooltip)
    # away_name_entry.bind("<Leave>", hide_name_tooltip)
    
def exit_application():
    root.destroy()
    root.quit()
    
def binding_manager(event):
    if not final:
        if event.char == 'p':
            increment_inning()
        elif event.char == 'b':
            increment_balls()
        elif event.char == 'k':
            increment_strikes()
        elif event.char == 'o':
            increment_outs()
        elif event.char == 'h':
            increment_hits()
            reset_count()
        elif event.char == 'e':
            increment_errors()
        elif event.char == 'r':
            reset_count()
        elif event.char == 's':
            score_run()
        elif event.char == 'c':
            clear_bases()
        elif event.char == '1':
            toggle_base(0)
        elif event.char == '2':
            toggle_base(1)
        elif event.char == '3':
            toggle_base(2)
        elif event.char == 'f':
            foul_ball()
        elif event.char == 'n':
            new_pitcher()

def foul_ball():
    global strikes, current_pitch_count
    if strikes < 2:
        increment_strikes()
    else:
        current_pitch_count += 1
        update_score()
    
    
def open_color_picker(e):
    # root = tk.Tk()
    # root.withdraw()  # Hide the main Tkinter window
    color = colorchooser.askcolor()[1]  # Ask the user to pick a color
    if color:
        canvas = e.widget
        for item in canvas.find_all():
            item_type=canvas.type(item)
            if item_type == 'rectangle':
                canvas.itemconfig(item, fill=color)
    # root.destroy()  # Close the hidden Tkinter window
    return color

def select_team_color(team):
    global home_team_color, away_team_color
    selected_color = open_color_picker()
    if team == "Home":
        home_team_color = selected_color
    elif team == "Away":
        away_team_color = selected_color
        
def rescale_image(path, factor=0.25):
    original = Image.open(path)
    new_width = round(factor * original.width)
    new_height = round(factor * original.height)
    return original.resize((new_width, new_height), Image.LANCZOS)

def shadow_color_finder(color, secondary = "#000000"):
    if not secondary == "#000000":
        base_shadow=shadow_color_finder(secondary)
    else:
        base_shadow = secondary
    base_shadow_r, base_shadow_g, base_shadow_b = hex_to_rgb(base_shadow)
    # print(base_shadow_r)
    if color[0] == '#':
        color_r, color_g, color_b = hex_to_rgb(color)
    else:
        color_r, color_g, color_b = color[0], color[1], color[2]
    
    return rgb_to_hex((base_shadow_r+color_r)//2, (base_shadow_g+color_g)//2, (base_shadow_b+color_b)//2)

def hex_to_rgb(hex_color):
    # Remove any '#' from the beginning of the hex color code
    hex_color = hex_color.lstrip('#')
    # Convert the hex color code to RGB values
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)

def rgb_to_hex(r, g, b):
    # Convert RGB values to a hexadecimal color code
    hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
    return hex_color

def toggle_base(base):
    global bases
    # Toggle the state of the base (True to False or False to True)
    bases[base] = not bases[base]
    
    update_base_indicators()
    
def update_base_indicators():
    global bases
    global basesImg
    indicator_arrangement = ''
    if bases[2]:
        indicator_arrangement = indicator_arrangement + '3-'
    else:
        indicator_arrangement = indicator_arrangement + '0-'
    if bases[1]:
        indicator_arrangement = indicator_arrangement + '2-'
    else:
        indicator_arrangement = indicator_arrangement + '0-'
    if bases[0]:
        indicator_arrangement = indicator_arrangement + '1-'
    else:
        indicator_arrangement = indicator_arrangement + '0-'  
    indicator_arrangement = indicator_arrangement + "bases.png"
    basesImg = ImageTk.PhotoImage(rescale_image(os.path.join(resource_folder, indicator_arrangement)))
    bases_indicator.config(image = basesImg)
    
    # Update the base indicators based on the values in the 'bases' dictionary
    first_base_indicator.select() if bases[0] else first_base_indicator.deselect()
    second_base_indicator.select() if bases[1] else second_base_indicator.deselect()
    third_base_indicator.select() if bases[2] else third_base_indicator.deselect()
    
    #bug updates
    bases_canvas.itemconfig(bases_indicator_bug, image = basesImg)
    
def update_out_indicator():
    global outs
    global outImg
    outs_arrangement = '-out.png'
    if outs == 0:
        outs_arrangement = '0'+outs_arrangement
    elif outs == 1:
        outs_arrangement = '1'+outs_arrangement
    elif outs == 2:
        outs_arrangement = '2'+outs_arrangement
    elif outs == 3:
        outs_arrangement = '3'+outs_arrangement        
    outImg = ImageTk.PhotoImage(rescale_image(os.path.join(resource_folder, outs_arrangement), 0.2))
    inn_canvas.itemconfig(outs_bug, image = outImg)
    
def update_half_indicator():
    global current_half
    global halfImg
    half_arrangement ='.png'
    if (current_half == 0 or current_half == 1) and not final:
        half_arrangement = 'top' + half_arrangement
    elif not final:
        half_arrangement = 'bottom' + half_arrangement
    else:
        half_arrangement = 'end' + half_arrangement
    halfImg = ImageTk.PhotoImage(rescale_image(os.path.join(resource_folder, half_arrangement), 0.12))
    count_canvas.itemconfig(half_bug, image = halfImg)

def end_game():
    global current_half
    global halfImg
    global final
    
    if not final:
        # outs_canvas.itemconfig(pitch_count_bug, text = "")
        final = True
        update_score()
        count_canvas.coords(inns_bug, 133//2+3, 67//2)
        count_canvas.itemconfig(inns_bug, text=f"F / {inning}")
    elif final:
        final = False
        update_score()
    
    
def update_score():
    # Update labels with the new values
    inning_label.config(text=f"Inning: {inning_halfs[current_half]} {inning}")
    home_score_label.config(text=f"{teams[0]}: {home_score}")
    away_score_label.config(text=f"{teams[1]}: {away_score}")
    count_label.config(text=f"{balls}-{strikes}")
    if not outs == 1:
        out_label.config(text=f"{outs} Outs")
    else:
        out_label.config(text=f"{outs} Out")
        
    controller_box_away_name.config(text=teams_short[1])
    controller_box_home_name.config(text=teams_short[0])
    controller_box_away_runs.config(text=away_score)
    controller_box_home_runs.config(text=home_score)
    controller_box_away_hits.config(text=away_hits)
    controller_box_home_hits.config(text=home_hits)
    controller_box_away_errors.config(text=away_errors)
    controller_box_home_errors.config(text=home_errors)
    
    update_base_indicators()
    update_scorebug() 

def update_scorebug():
    team_canvas.itemconfig(away_canvas_rectangle, fill=away_team_color)
    team_canvas.itemconfig(home_canvas_rectangle, fill=home_team_color)

    team_canvas.itemconfig(away_canvas_team_name, text=teams[1].upper(), fill=away_team_color2)
    # team_canvas.itemconfig(away_canvas_team_name_shadow, text=teams[1].upper(), fill=shadow_color_finder(away_team_color, away_team_color2))
    team_canvas.itemconfig(home_canvas_team_name, text=teams[0].upper(), fill=home_team_color2)
    # team_canvas.itemconfig(home_canvas_team_name_shadow, text=teams[0].upper(), fill=shadow_color_finder(home_team_color, home_team_color2))
    
    score_canvas.itemconfig(away_score_text, text=away_score)
    score_canvas.itemconfig(home_score_text, text=home_score)
    
    inn_canvas.itemconfig(count_bug, text=f"{balls} - {strikes}")
    
    count_canvas.coords(inns_bug, 133//2+10, 67//2)
    
    outs_canvas.itemconfig(pitch_count_bug, text=f"{current_pitch_count}")
        
    
    if  current_half==1 or current_half == 3 or final:
        inn_canvas.itemconfig(count_bug, fill ='black')
    else:
        inn_canvas.itemconfig(count_bug, fill ='white')
        
    if show_pitch_count or current_pitch_count == 0 or current_half==1 or current_half == 3 or final:
        outs_canvas.itemconfig(pitching_label, fill = 'black')
        outs_canvas.itemconfig(pitch_count_bug, fill = 'black')
    else:
        outs_canvas.itemconfig(pitching_label, fill = 'white')
        outs_canvas.itemconfig(pitch_count_bug, fill = 'white')
        
    # if not outs == 1:
    #     inn_canvas.itemconfig(outs_bug,text=f"{outs} OUTS")
    # else:
    #     inn_canvas.itemconfig(outs_bug,text=f"{outs} OUT")
    
    # print("Home Pitches: "+str(pitch_count[0]))
    # print("Away Pitches: "+str(pitch_count[1]))
    count_canvas.itemconfig(inns_bug, text=f"{inning}")
    update_out_indicator()
    update_half_indicator()
    
def show_box_score():
    def invert_color (color):
        r, g, b = hex_to_rgb(color)
        r = 255-r
        g = 255-g
        b = 255-b
        return rgb_to_hex(r, g, b)
    def palify_color(color):
        r, g, b = hex_to_rgb(color)
        r = (255+r)//2
        g = (255+g)//2
        b = (255+b)//2
        return rgb_to_hex(r, g, b)
        
    def alternate_color(color1, color2, team_color):
        c1_r, c1_g, c1_b = hex_to_rgb(color1)
        c2_r, c2_g, c2_b = hex_to_rgb(color2)
        
        c_r = c1_r-c2_r
        c_g = c1_g-c2_g
        c_b = c1_b-c2_b
        
        t_r, t_g, t_b = hex_to_rgb(team_color)
        
        out_r = t_r + c_r
        out_g = t_g + c_g
        out_b = t_b + c_b
        
        if out_r > 255:
            out_r =255
        if out_b > 255:
            out_b =255
        if out_g > 255:
            out_g =255
        
        return rgb_to_hex(out_r, out_g, out_b)
        
    box_score_window = tk.Toplevel(root)
    box_score_window.title("Box Score")
    
    cols = len(home_inning_runs)
    
    if (not len(home_inning_runs) == len(away_inning_runs)) and (home_score < away_score):
        # away_inning_runs.pop()
        cols -= 1
    elif (not len(home_inning_runs) == len(away_inning_runs)) and (home_score > away_score):
        home_inning_runs.append(0)
        
    box_score_height = 250
    box_score_width = 750
    
    # home_box_rects = []
    # away_box_rects = []
    
    box_width = box_score_width // (cols+5)
    box_score_width = box_width*(cols+5)
    box_head_height = 50
    box_height = (box_score_height - box_head_height) //2
    
    # home_rects = []
    # away_rects = []
    # head_rects = []
    
    box_score_canvas = tk.Canvas(box_score_window, height = box_score_height, width = box_score_width)
    
    box_font = font.Font(family="Arial Narrow", size=36)
    box_name_font = font.Font(family="arial", size=36, weight="bold")
    
    column_color1 = mcolors.XKCD_COLORS["xkcd:grey"] #should be darker
    column_color2 = mcolors.CSS4_COLORS["grey"]
    j=0
    
    for i in range(cols+3):
        if i==0: #3 cols wide
            rect = box_score_canvas.create_rectangle(0, box_head_height, box_width * 3, box_head_height+box_height, fill = away_team_color, outline = "")
            rect = box_score_canvas.create_rectangle(0, box_head_height+box_height, box_width * 3, box_head_height+box_height*2, fill = home_team_color, outline = "")
            if cols > 6:
                away_box_shadow = box_score_canvas.create_text(box_width*3-3, box_height//2+box_head_height+2, text=teams_short[1].upper(), fill=shadow_color_finder(away_team_color, away_team_color2), font=box_name_font, anchor='e')
                away_box_text = box_score_canvas.create_text(box_width*3-5, box_height//2+box_head_height, text=teams_short[1].upper(), fill=away_team_color2, font=box_name_font, anchor='e')
                home_box_shadow = box_score_canvas.create_text(box_width*3-3,box_height//2*3+box_head_height+2, text=teams_short[0].upper(), fill=shadow_color_finder(home_team_color, home_team_color2), font=box_name_font, anchor='e')
                home_box_text = box_score_canvas.create_text(box_width*3-5, box_height//2*3+box_head_height, text=teams_short[0].upper(), fill=home_team_color2, font=box_name_font, anchor='e')
            else:
                away_box_shadow = box_score_canvas.create_text(box_width*3-3, box_height//2+box_head_height+2, text=teams[1].upper(), fill=shadow_color_finder(away_team_color, away_team_color2), font=box_name_font, anchor='e')
                away_box_text = box_score_canvas.create_text(box_width*3-5, box_height//2+box_head_height, text=teams[1].upper(), fill=away_team_color2, font=box_name_font, anchor='e')
                home_box_shadow = box_score_canvas.create_text(box_width*3-3,box_height//2*3+box_head_height+2, text=teams[0].upper(), fill=shadow_color_finder(home_team_color, home_team_color2), font=box_name_font, anchor='e')
                home_box_text = box_score_canvas.create_text(box_width*3-5, box_height//2*3+box_head_height, text=teams[0].upper(), fill=home_team_color2, font=box_name_font, anchor='e')
                
        elif i<cols:
            # Headings
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color2, outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color1, outline = "")
            head_text = box_score_canvas.create_text(box_width // 2 + box_width * (i+2), box_head_height // 2, text=i, fill='white', font=box_font)
            
            # Away 
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = away_team_color, outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = alternate_color(column_color1, column_color2, away_team_color), outline = "")
            try:
                away_text_shadow = box_score_canvas.create_text(box_width*(i+2)+box_width // 2 +16, box_height//2+box_head_height+2, text=away_inning_runs[j], fill=shadow_color_finder(away_team_color, away_team_color2), font=box_name_font, anchor='e')
                away_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2+box_head_height, text=away_inning_runs[j], fill=away_team_color2, font=box_name_font)
            except Exception as e:
                1
            # Home
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = home_team_color, outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = alternate_color(column_color1, column_color2, home_team_color), outline = "")
            try:
                home_text_shadow = box_score_canvas.create_text((box_width*(i+2)+box_width // 2)+16, box_height//2*3+box_head_height+2, text=home_inning_runs[j], fill=shadow_color_finder(home_team_color, home_team_color2), font=box_name_font, anchor='e')
                home_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2*3+box_head_height, text=home_inning_runs[j], fill=home_team_color2, font=box_name_font)
            except Exception as e:
                1
            j += 1
            
        elif i == cols:
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color2, outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color1, outline = "")
            head_text = box_score_canvas.create_text(box_width // 2 + box_width * (i+2), box_head_height // 2, text="R", fill='white', font=box_font)
        
            # Away 
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = palify_color(away_team_color2), outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = palify_color(alternate_color(column_color1, column_color2, away_team_color2)), outline = "")
            try:
                away_text_shadow = box_score_canvas.create_text((box_width*(i+2)+box_width // 2)+16, box_height//2+box_head_height+2, text=away_score, fill=shadow_color_finder(away_team_color, away_team_color2), font=box_name_font, anchor='e')
                away_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2+box_head_height, text=away_score, fill=away_team_color, font=box_name_font)
            except Exception as e:
                1
            # Home
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = palify_color(home_team_color2), outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = palify_color(alternate_color(column_color1, column_color2, home_team_color2)), outline = "")
            try:
                home_text_shadow = box_score_canvas.create_text((box_width*(i+2)+box_width // 2)+16, box_height//2*3+box_head_height+2, text=home_score, fill=shadow_color_finder(home_team_color, home_team_color2), font=box_name_font, anchor='e')
                home_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2*3+box_head_height, text=home_score, fill=home_team_color, font=box_name_font)
            except Exception as e:
                1
        
        elif i ==  cols+1:
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color2, outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color1, outline = "")
            head_text = box_score_canvas.create_text(box_width // 2 + box_width * (i+2), box_head_height // 2, text="H", fill='white', font=box_font)
        
            # Away 
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = palify_color(away_team_color2), outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = palify_color(alternate_color(column_color1, column_color2, away_team_color2)), outline = "")
            try:
                away_text_shadow = box_score_canvas.create_text(box_width*(i+2)+box_width // 2 +16, box_height//2+box_head_height+2, text=away_hits, fill=shadow_color_finder(away_team_color2, away_team_color), font=box_name_font, anchor='e')
                away_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2+box_head_height, text=away_hits, fill=away_team_color, font=box_name_font)
            except Exception as e:
                1
            # Home
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = palify_color(home_team_color2), outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = palify_color(alternate_color(column_color1, column_color2, home_team_color2)), outline = "")
            try:
                home_text_shadow = box_score_canvas.create_text((box_width*(i+2)+box_width // 2)+16, box_height//2*3+box_head_height+2, text=home_hits, fill=shadow_color_finder(home_team_color, home_team_color2), font=box_name_font, anchor='e')
                home_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2*3+box_head_height, text=home_hits, fill=home_team_color, font=box_name_font)
            except Exception as e:
                1
        elif i == cols+2:
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color2, outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), 0, box_width * (i+3), box_head_height, fill = column_color1, outline = "")
            head_text = box_score_canvas.create_text(box_width // 2 + box_width * (i+2), box_head_height // 2, text="E", fill='white', font=box_font)
        
            # Away 
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = palify_color(away_team_color2), outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height, box_width * (i+3), box_head_height+box_height, fill = palify_color(alternate_color(column_color1, column_color2, away_team_color2)), outline = "")
            try:
                away_text_shadow = box_score_canvas.create_text(box_width*(i+2)+box_width // 2 +16, box_height//2+box_head_height+2, text=away_errors, fill=shadow_color_finder(away_team_color2, away_team_color), font=box_name_font, anchor='e')
                away_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2+box_head_height, text=away_errors, fill=away_team_color, font=box_name_font)
            except Exception as e:
                1
            # Home
            if i%2==0:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = palify_color(home_team_color2), outline = "")
            else:
                rect = box_score_canvas.create_rectangle(box_width * (i+2), box_head_height+box_height, box_width * (i+3),  box_head_height+box_height*2, fill = palify_color(alternate_color(column_color1, column_color2, home_team_color2)), outline = "")
            try:
                home_text_shadow = box_score_canvas.create_text((box_width*(i+2)+box_width // 2)+16, box_height//2*3+box_head_height+2, text=home_errors, fill=shadow_color_finder(home_team_color2, home_team_color), font=box_name_font, anchor='e')
                home_text = box_score_canvas.create_text(box_width*(i+2)+box_width // 2, box_height//2*3+box_head_height, text=home_errors, fill=home_team_color, font=box_name_font)
            except Exception as e:
                1

    box_score_canvas.pack()
    return False
    
# Create the main tkinter window
root = tk.Tk()
root.title("Baseball Scorebug Controller")

root.protocol("WM_DELETE_WINDOW", exit_application)

# # Load your icon image using PhotoImage (replace with the correct path)
# icon_image = tk.PhotoImage(os.path.join(resource_folder, 'calcIcon.png'))

# # Set the window's icon
# root.iconphoto(False, icon_image)

# Labels to display score, inning, etc.
inning_label = tk.Label(root, text=f"Inning: {inning}")
home_score_label = tk.Label(root, text=f"Home: {home_score}")
away_score_label = tk.Label(root, text=f"Away: {away_score}")
count_label = tk.Label(root, text=f"{balls}-{strikes}")
out_label = tk.Label(root, text=f"{outs} Outs")

# Base indicators
basesImg = ImageTk.PhotoImage(rescale_image(os.path.join(resource_folder, '0-0-0-bases.png')))
bases_indicator = tk.Label(root, image = basesImg)

# Base indicators (toggle buttons)
first_base_indicator = tk.Checkbutton(root, text="1st", command=lambda: toggle_base(0))
second_base_indicator = tk.Checkbutton(root, text="2nd", command=lambda: toggle_base(1))
third_base_indicator = tk.Checkbutton(root, text="3rd", command=lambda: toggle_base(2))


# Buttons for user interaction
increment_inning_button = tk.Button(root, text="Increment Inning", command=increment_inning)
decrement_inning_button = tk.Button(root, text="Decrement Inning", command=decrement_inning)
increment_home_score_button = tk.Button(root, text="Increment Home Score", command=increment_home_score)
decrement_home_score_button = tk.Button(root, text="Decrement Home Score", command=decrement_home_score)
increment_away_score_button = tk.Button(root, text="Increment Away Score", command=increment_away_score)
decrement_away_score_button = tk.Button(root, text="Decrement Away Score", command=decrement_away_score)
increment_ball_button = tk.Button(root, text="Increment Balls", command=increment_balls)
decrement_ball_button = tk.Button(root, text="Decrement Balls", command=decrement_balls)
increment_strike_button = tk.Button(root, text="Increment Strikes", command=increment_strikes)
decrement_strike_button = tk.Button(root, text="Decrement Strikes", command=decrement_strikes)
increment_out_button = tk.Button(root, text="Increment Outs", command=increment_outs)
decrement_out_button = tk.Button(root, text="Decrement Outs", command=decrement_outs)

run_button = tk.Button(root, text="Score Run", command=score_run)
clear_bases_button = tk.Button(root, text="Clear Bases", command=clear_bases)
reset_count_button = tk.Button(root, text="Reset Count", command=reset_count)

# Key bindings
root.bind('p', binding_manager)
root.bind('b', binding_manager)
root.bind('k', binding_manager)
root.bind('o', binding_manager)
root.bind('h', binding_manager)
root.bind('e', binding_manager)
root.bind('r', binding_manager)
root.bind('s', binding_manager)
root.bind('c', binding_manager)
root.bind('1', binding_manager)
root.bind('2', binding_manager)
root.bind('3', binding_manager)
root.bind('f', binding_manager)
root.bind('n', binding_manager)

# Grid layout: Organize widgets in rows and columns
inning_label.grid(row=0, column=0)
home_score_label.grid(row=1, column=0)
away_score_label.grid(row=2, column=0)

increment_inning_button.grid(row=0, column=1)
decrement_inning_button.grid(row=0, column=2)
increment_home_score_button.grid(row=1, column=1)
decrement_home_score_button.grid(row=1, column=2)
increment_away_score_button.grid(row=2, column=1)
decrement_away_score_button.grid(row=2, column=2)

bases_indicator.grid(row=0, column=5, rowspan=3, columnspan=3)
first_base_indicator.grid(row=4, column=5)
second_base_indicator.grid(row=4, column=6)
third_base_indicator.grid(row=4, column=7)
run_button.grid(row=5, column=5, columnspan=3)
clear_bases_button.grid(row=6, column=5, columnspan=3)

increment_ball_button.grid(row=5, column=1)
decrement_ball_button.grid(row=5, column=2)
increment_strike_button.grid(row=6, column=1)
decrement_strike_button.grid(row=6, column=2)
increment_out_button.grid(row=7, column=1)
decrement_out_button.grid(row=7, column=2)
reset_count_button.grid(row=8, column=1, columnspan=2)

count_label.grid(row=6, column=0)
out_label.grid(row=7, column=0)

controller_box_r_label = tk.Label(root, text="R")
controller_box_h_label = tk.Label(root, text="H")
controller_box_e_label = tk.Label(root, text="E")

controller_box_away_name = tk.Label(root, text=teams_short[1])
controller_box_home_name = tk.Label(root, text=teams_short[1])
controller_box_away_runs = tk.Label(root, text=away_score)
controller_box_home_runs = tk.Label(root, text=home_score)
controller_box_away_hits = tk.Label(root, text=away_hits)
controller_box_home_hits = tk.Label(root, text=home_hits)
controller_box_away_errors = tk.Label(root, text=away_errors)
controller_box_home_errors = tk.Label(root, text=home_errors)
increment_hits_button = tk.Button(root, text="Increment Hits", command=increment_hits)
decrement_hits_button = tk.Button(root, text="Decrement Hits", command=decrement_hits)
increment_errors_button = tk.Button(root, text="Increment Errors", command=increment_errors)
decrement_errors_button = tk.Button(root, text="Decrement Errors", command=decrement_errors)

# Conntroller Box Score
controller_box_r_label.grid(row=0, column=10)
controller_box_h_label.grid(row=0, column=11)
controller_box_e_label.grid(row=0, column=12)

controller_box_away_name.grid(row=1, column= 9)
controller_box_home_name.grid(row=2, column= 9)
controller_box_away_runs.grid(row=1, column= 10)
controller_box_home_runs.grid(row=2, column= 10)
controller_box_away_hits.grid(row=1, column= 11)
controller_box_home_hits.grid(row=2, column= 11)
controller_box_away_errors.grid(row=1, column= 12)
controller_box_home_errors.grid(row=2, column= 12)
increment_hits_button.grid(row=3, column= 11, columnspan=2)
decrement_hits_button.grid(row=3, column= 9, columnspan=2)
increment_errors_button.grid(row=4, column= 11, columnspan=2)
decrement_errors_button.grid(row=4, column= 9, columnspan=2)


pitch_count_indicator = tk.Checkbutton(root, text="Hide Pitch Count", command=lambda: toggle_pitch_count())
pitch_count_indicator. grid(row=5, column=10)
new_pitcher_button = tk.Button(root, text = "New Pitcher", command = new_pitcher)
new_pitcher_button.grid(row =5, column=11, columnspan=2)
finalize_button = tk.Button(root, text = "End Game", command=end_game)
finalize_button.grid(row=6, column=9, columnspan = 4, rowspan=2)

# Spacer
spacer_label = tk.Label(root, text="     ")
spacer_label.grid(row=0, column=3)
spacer_label.grid(row=0, column=9)

# Menu
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New Game", command=new_game)
file_menu.add_command(label="Exit", command=exit_application)

settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Configure Teams", command=team_config)

game_over_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_command(label='Game End', command=show_box_score)

#################
# Scorebug
################
scorebug = tk.Toplevel(root)
scorebug.title("Scorebug")

team_bug_font = font.Font(family="Arial Black", size=50, weight='bold')
count_bug_font = font.Font(family="Arial", size=25, weight='bold')
inns_bug_font = font.Font(family="Arial Narrow", size=36)
pitch_bug_font = font.Font(family="Arial", size=14)

canvas_width = 500
canvas_height = 200
offset=3
team_canvas = tk.Canvas(scorebug, width=canvas_width, height=canvas_height)
away_canvas_rectangle = team_canvas.create_rectangle(0, 0, canvas_width+50, canvas_height//2+50, fill=away_team_color, outline="")
# away_canvas_team_name_shadow = team_canvas.create_text(canvas_width-15+offset,canvas_height//4+offset, text=teams[1], fill=shadow_color_finder(away_team_color), font=team_bug_font, anchor='e')
away_canvas_team_name = team_canvas.create_text(canvas_width-15,canvas_height//4, text=teams[1], fill='white', font=team_bug_font, anchor='e')

home_canvas_rectangle = team_canvas.create_rectangle(0, canvas_height//2, canvas_width+50, canvas_height//1+50, fill=home_team_color, outline="")
# home_canvas_team_name_shadow = team_canvas.create_text(canvas_width-15+offset,150+offset, text=teams[0], fill=shadow_color_finder(home_team_color, home_team_color2), font=team_bug_font, anchor='e')
home_canvas_team_name = team_canvas.create_text(canvas_width-15,150, text=teams[0], fill=home_team_color2, font=team_bug_font, anchor='e')
team_canvas.grid(row=0, column=0, padx=0, pady=0, rowspan=2)

score_canvas = tk.Canvas(scorebug, width=canvas_height//2, height=canvas_height)
away_score_text = score_canvas.create_text(canvas_height//4, canvas_height//4, text=away_score, fill='black', font=team_bug_font)
home_score_text = score_canvas.create_text(canvas_height//4, 150, text=home_score, fill='black', font=team_bug_font)
score_canvas.grid(row=0, column=1, rowspan=2, padx=0, pady=0)

bases_canvas = tk.Canvas(scorebug, width=133, height=133)
bases_bg=bases_canvas.create_rectangle(-15,-15,150,150, fill='black')
basesImg = ImageTk.PhotoImage(rescale_image(os.path.join(resource_folder, '0-0-0-bases.png')))
bases_indicator_bug = bases_canvas.create_image(133//2+3,133//2, image=basesImg)
bases_canvas.grid(row=0, column=2)

count_canvas = tk.Canvas(scorebug, width=133, height=67)
count_bg = count_canvas.create_rectangle(0,0,133,67, fill='black')
# count_bug = count_canvas.create_text(133//2+3, 67//2, text=f"{balls} - {strikes}", fill='white', font=count_bug_font)
# inns_bug = count_canvas.create_text(133//2+3, 67//2, text=f"Inning: {inning_halfs[current_half].upper()} {inning}", fill='white', font=count_bug_font)

halfImg = ImageTk.PhotoImage(rescale_image(os.path.join(resource_folder, 'bottom.png')))
half_bug = count_canvas.create_image(133//2-15, 67//2+2, image=halfImg)
inns_bug = count_canvas.create_text(133//2+10, 67//2+2, text=f"{inning}", fill='white', font=count_bug_font)

count_canvas.grid(row=1,column=2)

inn_canvas = tk.Canvas(scorebug, width=133, height=133)
inn_bg=inn_canvas.create_rectangle(-15,-15,150,150, fill='black')
count_bug = inn_canvas.create_text(133//2+3, 133//2-10, text=f"{balls} - {strikes}", fill='white', font=inns_bug_font)
# inns_bug = inn_canvas.create_text(133//2+3, 133//2-10, text=f"Inning: {inning_halfs[current_half].upper()} {inning}", fill='white', font=inns_bug_font)
outImg = ImageTk.PhotoImage(rescale_image(os.path.join(resource_folder, '3-out.png')))
outs_bug = inn_canvas.create_image(133//2+3, 67//2*3+10, image=outImg)
# outs_bug = inn_canvas.create_text(133//2+3, 67//2*3+10, text=f"{outs} Outs", fill='white', font=count_bug_font)

inn_canvas.grid(row=0, column=3)

outs_canvas = tk.Canvas(scorebug, width=133, height=67)
outs_bg = outs_canvas.create_rectangle(0,0,133,67, fill='black')
# outs_bg1 = outs_canvas.create_rectangle(0,0,(133-5)//2,67, fill='black')
# outs_bg2 = outs_canvas.create_rectangle((133+5)//2,0,133,67, fill='black')

# outs_bug = outs_canvas.create_text(133//2+3, 67//2, text=f"{outs} Outs", fill='white', font=count_bug_font)
# count_bug = outs_canvas.create_text(133//2+3, 67//2, text=f"{balls} - {strikes}", fill='white', font=count_bug_font)

pitching_label = outs_canvas.create_text(133//2+3, 67//4, text="Pitches:", fill="white", font=pitch_bug_font)
# pitch_count_bug =outs_canvas.create_text((133)//2+3, 67//3*2, text=f"{current_pitch_count}", fill="white", font=count_bug_font)
pitch_count_bug =outs_canvas.create_text((133)//2+3, 67//3*2, text=f"{current_pitch_count}", fill="white", font=count_bug_font)

outs_canvas.grid(row=1, column=3)

update_score()
update_scorebug()

# Force focus upon opening
root.focus_force()

# Run the tkinter main loop
root.mainloop()
