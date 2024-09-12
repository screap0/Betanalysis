import requests
from bs4 import BeautifulSoup
import customtkinter as ctk
import numpy as np
import tkinter.messagebox as mb

def change_turkish_character(team_name):
    team_name = team_name.replace("ı", "i")
    team_name = team_name.replace("İ", "I")
    team_name = team_name.replace("ö", "o")
    team_name = team_name.replace("ü", "u")
    team_name = team_name.replace("ğ", "g")
    team_name = team_name.replace("ş", "s")
    team_name = team_name.replace("ç", "c")
    return team_name.replace(" ", "-")

def to_lowercase(team_name):
    return team_name.lower()

def getmatches_info(team):
    url = f"https://www.sporx.com/{team}-fiksturu-ve-mac-sonuclari"
    response = requests.get(url)
    
    # Durum kodunu kontrol et
    if response.status_code != 200:
        print(f"URL erişim hatası: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    matches = soup.find_all("tr")
    
    if not matches:
        print(f"{team} için maç bilgileri bulunamadı.")
        return None
    
    number_of_wins = 0
    total_goal = 0
    last_match_score = None
    match_meter = 0
    team_matches = []

    for match in matches:
        # Skor elementini bul ve hata yakalama ekle
        score_element = match.find("a", class_="d-block rounded bg-sporx text-white fw-bolder py-1 px-1 text-nowrap")
        if score_element:
            score = score_element.get_text(strip=True)
            goal_number = score.split("-")
            if len(goal_number) == 2 and goal_number[0].strip() and goal_number[1].strip():
                try:
                    home_team_goal = int(goal_number[0])
                    away_goal = int(goal_number[1]) 
                    team_matches.append(home_team_goal)
                    team_matches.append(away_goal)
                    match_meter += 1
                except ValueError:
                    print(f"Skor hatası: {score}")
                    continue

                home_team = match.find("td", class_="text-start w-25").find("a").get_text(strip=True)
                away = match.find("td", class_="text-end w-25").find("a").get_text(strip=True)
                if team.lower() == change_turkish_character(home_team.lower()):
                    total_goal += home_team_goal
                    if home_team_goal > away_goal:
                        number_of_wins += 1
                    last_match_score = f"Son Maç: {home_team} - {score} {away}"
                elif team.lower() == change_turkish_character(away.lower()):
                    total_goal += away_goal
                    if home_team_goal < away_goal:
                        number_of_wins += 1
                    last_match_score = f"Son Maç: {home_team} - {score} {away}"

    if match_meter == 0:
        print(f"{team} için geçerli maç verisi bulunamadı.")
        return 0, 0, None, 0, []
    else:
        return number_of_wins, total_goal, last_match_score, match_meter, team_matches

def analyze_performance(team_matches, match_meter):
    if match_meter == 0:
        return {
            'win_count': 0,
            'draw_count': 0,
            'loss_count': 0,
            'avg_goals_scored': 0,
            'avg_goals_conceded': 0,
            'goals_conceded': []
        }

    win_count = sum(1 for i in range(0, len(team_matches) - 1, 2) if team_matches[i] > team_matches[i + 1])
    draw_count = sum(1 for i in range(0, len(team_matches) - 1, 2) if team_matches[i] == team_matches[i + 1])
    loss_count = sum(1 for i in range(0, len(team_matches) - 1, 2) if team_matches[i] < team_matches[i + 1])

    total_matches = match_meter
    avg_goals_scored = sum(team_matches[i] for i in range(0, len(team_matches), 2)) / total_matches if total_matches else 0
    avg_goals_conceded = sum(team_matches[i + 1] for i in range(0, len(team_matches), 2)) / total_matches if total_matches else 0
    goals_conceded = [team_matches[i + 1] for i in range(0, len(team_matches), 2)]
    
    

    return {
        'win_count': win_count,
        'draw_count': draw_count,
        'loss_count': loss_count,
        'avg_goals_scored': avg_goals_scored,
        'avg_goals_conceded': avg_goals_conceded,
        'goals_conceded': goals_conceded
        
    }

def two_team_analysis(result_label):
    team1 = to_lowercase(change_turkish_character(team1_entry.get()))
    team2 = to_lowercase(change_turkish_character(team2_entry.get()))
    
    if not team1 or not team2:
        result_label.configure(text="Lütfen takımları girin.")
        return

    if team1 == team2:
        result_label.configure(text="Aynı takımı seçtiniz. Lütfen farklı takımlar seçin.")
        return

    team1_info = getmatches_info(team1)
    team2_info = getmatches_info(team2)
    
    if team1_info is None or team2_info is None:
        result_label.configure(text="Bir veya daha fazla takım için bilgi alınamadı.")
        return

    number_of_wins_team1, total_goal_team1, last_match_score_team1, match_meter_team1, team1_matches = team1_info
    number_of_wins_team2, total_goal_team2, last_match_score_team2, match_meter_team2, team2_matches = team2_info
    
    if match_meter_team1 == 0 or match_meter_team2 == 0:
        result_label.configure(text="Bir veya her iki takım için geçerli maç verisi bulunamadı.")
        return

    team1_performance = analyze_performance(team1_matches, match_meter_team1)
    team2_performance = analyze_performance(team2_matches, match_meter_team2)

    # Tahmini gol hesaplama
    avg_goals_scored_team1 = team1_performance['avg_goals_scored']
    avg_goals_scored_team2 = team2_performance['avg_goals_scored']
    avg_goals_conceded_team1 = team1_performance['avg_goals_conceded']
    avg_goals_conceded_team2 = team2_performance['avg_goals_conceded']
    min_match_meter = min(match_meter_team1, match_meter_team2)

       # Son 3 maçın gol bilgileri
    recent_goals_scored_team1 = team1_matches[-3:] if match_meter_team1 > 3 else team1_matches
    recent_goals_scored_team2 = team2_matches[-3:] if match_meter_team2 > 3 else team2_matches
    older_goals_scored_team1 = team1_matches[:-3] if match_meter_team1 > 3 else []
    older_goals_scored_team2 = team2_matches[:-3] if match_meter_team2 > 3 else []

    recent_goals_conceded_team1 = [team1_matches[i + 1] for i in range(-3, 0, 2)] if match_meter_team1 > 2 else [team1_matches[i + 1] for i in range(0, len(team1_matches), 2)]
    recent_goals_conceded_team2 = [team2_matches[i + 1] for i in range(-3, 0, 2)] if match_meter_team2 > 2 else [team2_matches[i + 1] for i in range(0, len(team2_matches), 2)]
    older_goals_conceded_team1 = [team1_matches[i + 1] for i in range(0, len(team1_matches) - 3, 2)] if match_meter_team1 > 3 else []
    older_goals_conceded_team2 = [team2_matches[i + 1] for i in range(0, len(team2_matches) - 3, 2)] if match_meter_team2 > 3 else []

    # Ağırlıklı ortalama hesaplama
    def weighted_average(recent, older, recent_weight, older_weight):
        recent_sum = sum(recent) * recent_weight
        older_sum = sum(older) * older_weight
        total_weight = recent_weight + older_weight
        return (recent_sum + older_sum) / total_weight if total_weight != 0 else 0

    weighted_avg_goals_scored_team1 = weighted_average(recent_goals_scored_team1, older_goals_scored_team1, 1.5, 0.5)
    weighted_avg_goals_scored_team2 = weighted_average(recent_goals_scored_team2, older_goals_scored_team2, 1.5, 0.5)
    weighted_avg_goals_conceded_team1 = weighted_average(recent_goals_conceded_team1, older_goals_conceded_team1, 1.5, 0.5)
    weighted_avg_goals_conceded_team2 = weighted_average(recent_goals_conceded_team2, older_goals_conceded_team2, 1.5, 0.5)

    # Basit bir modelleme: Her iki takımın ortalama gol sayıları ve rakiplerinin yenilen gollerini dikkate alarak tahmin yapma
    home_advantage = 1
    away_disadvantage = 0.9
    predicted_team1_goal = (avg_goals_scored_team1+avg_goals_conceded_team2 )* home_advantage
    predicted_team2_goal = (avg_goals_scored_team2+avg_goals_conceded_team1 ) * away_disadvantage

    # Gol tahminlerini belirle
    team1_goal = round(predicted_team1_goal)
    team2_goal = round(predicted_team2_goal)

    # Olumsuz gol sayılarını sıfıra sabitle
    team1_goal = max(0, team1_goal)
    team2_goal = max(0, team2_goal)

    # Sonuç metnini oluştur
    predicted_result = f"Tahmini Maç Sonucu: {team1.capitalize()} {team1_goal} - {team2_goal} {team2.capitalize()}"



    # Form durumu
    team1_form = "favori" if number_of_wins_team1 > number_of_wins_team2 else "normal"
    team2_form = "favori" if number_of_wins_team2 > number_of_wins_team1 else "normal"

    result = f"**{team1.capitalize()} Takımı Form Durumu:** {team1_form}\n"
    result += f"**{team1.capitalize()} Takımı Performans Analizi ({match_meter_team1} Maç):**\n"
    result += f"Kazanma: {team1_performance['win_count']}\n"
    result += f"Beraberlik: {team1_performance['draw_count']}\n"
    result += f"Mağlubiyet: {team1_performance['loss_count']}\n"
    result += f"Maç Başına Ortalama Atılan Gol: {team1_performance['avg_goals_scored']:.2f}\n"
    result += f"Maç Başına Ortalama Yenilen Gol: {team1_performance['avg_goals_conceded']:.2f}\n"
    result += f"{team1.capitalize()} Takımı Son Maçı: {last_match_score_team1}\n\n"

    result += f"**{team2.capitalize()} Takımı Form Durumu:** {team2_form}\n"
    result += f"**{team2.capitalize()} Takımı Performans Analizi ({match_meter_team2} Maç):**\n"
    result += f"Kazanma: {team2_performance['win_count']}\n"
    result += f"Beraberlik: {team2_performance['draw_count']}\n"
    result += f"Mağlubiyet: {team2_performance['loss_count']}\n"
    result += f"Maç Başına Ortalama Atılan Gol: {team2_performance['avg_goals_scored']:.2f}\n"
    result += f"Maç Başına Ortalama Yenilen Gol: {team2_performance['avg_goals_conceded']:.2f}\n"
    result += f"{team2.capitalize()} Takımı Son Maçı: {last_match_score_team2}\n\n"

    result += f"\n**{predicted_result}**"

    # Sonuçları result_label'a yazdır
    result_label.configure(text=result)
    
# GUI'yi başlat
root = ctk.CTk()
root.title("Futbol Analiz Programı")
root.geometry("500x700")

# Başlık çerçevesi
header_frame = ctk.CTkFrame(root, corner_radius=10, bg_color="#1F1F1F")  # Koyu gri arka plan
header_frame.pack(padx=20, pady=20, fill="x")

# Başlık etiketi
header_label = ctk.CTkLabel(header_frame, text="Futbol Takımı Analiz Programı", font=("Helvetica", 24, "bold"), text_color="white")
header_label.pack(pady=10)

# Ana içerik çerçevesi
frame = ctk.CTkFrame(root, corner_radius=10, bg_color="#2C2C2C")  # Koyu gri arka plan
frame.pack(padx=20, pady=10, fill="both", expand=True)

# Takım etiketleri ve giriş alanları
team1_label = ctk.CTkLabel(frame, text="Ev Sahibi Takım:", font=("Helvetica", 16, "bold"), text_color="white")
team1_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

team1_entry = ctk.CTkEntry(frame, font=("Helvetica", 16), fg_color="#3C3C3C", text_color="white")  # Koyu gri giriş alanı
team1_entry.grid(row=0, column=1, padx=10, pady=10)

team2_label = ctk.CTkLabel(frame, text="Deplasman Takım:", font=("Helvetica", 16, "bold"), text_color="white")
team2_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

team2_entry = ctk.CTkEntry(frame, font=("Helvetica", 16), fg_color="#3C3C3C", text_color="white")  # Koyu gri giriş alanı
team2_entry.grid(row=1, column=1, padx=10, pady=10)

# Analiz butonu
analysis_button = ctk.CTkButton(frame, text="Analiz Yap", command=lambda: two_team_analysis(result_text), font=("Helvetica", 16, "bold"), corner_radius=8, fg_color="#4CAF50", text_color="white")  # Yeşil buton
analysis_button.grid(row=2, column=0, columnspan=2, pady=20)



# Sonuç etiketi
result_text = ctk.CTkLabel(frame, text="", wraplength=750, anchor="w", justify="left", font=("Helvetica", 14), text_color="white")
result_text.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()