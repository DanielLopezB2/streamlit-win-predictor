import pandas as pd
import pickle
import streamlit as st
from scipy.stats import poisson

dict_table = pickle.load(open('dict_table', 'rb'))
df_fixture = pd.read_csv('clean_fifa_worldcup_fixture.csv')
df_historical_data = pd.read_csv('clean_fifa_worldcup_matches.csv')


##Title
st.title('Probabilidad de Victoria de Selecciones Nacionales de Fútbol')
st.write('Este es un predictor de ganadores en posibles partidos de fútbol de selecciones nacionales. **Datos tomados hasta el 2021.**')


##Sidebar
st.sidebar.header('Campos de Entrada')

df_team_name = df_historical_data[['HomeTeam']]

unique_team = df_team_name[:902].drop_duplicates()

first_team = st.sidebar.selectbox(
    'Equipo Local',
    (unique_team))

second_team = st.sidebar.selectbox(
    'Equipo Visitante',
    (unique_team))


##Main
df_home = df_historical_data[['HomeTeam', 'HomeGoals', 'AwayGoals']]
df_away = df_historical_data[['AwayTeam', 'HomeGoals', 'AwayGoals']]

##Rename columns
df_home = df_home.rename(columns={'HomeTeam': 'Team', 'HomeGoals': 'GoalsScored', 'AwayGoals': 'GoalsConceded'})

df_away = df_away.rename(columns={'AwayTeam': 'Team', 'HomeGoals': 'GoalsConceded', 'AwayGoals': 'GoalsScored'})

##Concat df_home and df_away, group by team and calculate the mean(media)
df_team_strength = pd.concat([df_home, df_away], ignore_index=True).groupby('Team').mean()

#Function predict_points
def predict_points(home, away):
    if home in df_team_strength.index and away in df_team_strength.index:
        #goals_scored * goals_conceded
        lamb_home = df_team_strength.at[home, 'GoalsScored'] * df_team_strength.at[away, 'GoalsConceded']

        lamb_away = df_team_strength.at[away, 'GoalsScored'] * df_team_strength.at[home, 'GoalsConceded']

        prob_home, prob_away, prob_draw = 0,0,0

        for x in range(0,11): #number of goals home team
            for y in range(0,11): #number of goals away team
                p = poisson.pmf(x, lamb_home) * poisson.pmf(y, lamb_away)
                
                if x == y:
                    prob_draw += p

                elif x > y:
                    prob_home += p

                else:
                    prob_away += p

        points_home = 3 * prob_home + prob_draw
        points_away = 3 * prob_away + prob_draw
        return (points_home, points_away)
    
    else:
        return(0, 0)



if st.sidebar.button('Enviar :soccer:'):

    st.subheader(f'Probalidad para el partido: {first_team} vs {second_team}')
    st.caption('Nota: Entre más alto sea el resultado, mayor es la probabilidad de ganar frente al rival.')

    df_prob = predict_points(first_team, second_team)

    points_home, points_away = predict_points(first_team, second_team)

    # Crear un DataFrame con los datos
    data = {'Equipo': [first_team, second_team], 'Resultado': [points_home, points_away]}
    df = pd.DataFrame(data, columns=['Equipo', 'Resultado'])

    st.table(df)


    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

else:
    pass