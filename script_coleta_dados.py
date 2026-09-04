import requests
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

TOMTOM_API_KEY = "r54fB0Vh7yaMDb6J106hskBDOFHDNkBf"
SUPABASE_URL = "https://pnfsopceeyasexodnnzv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuZnNvcGNlZXlhc2V4b2Rubnp2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc3NjU4NTcsImV4cCI6MjEwMzM0MTg1N30._KUa9diFkbOhnUJV2mxNLKjp2JJnHrYTtL5OWaSG9EM" # Utilizando autenticação via anon key

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

pontos_monitoramento = [
    # 1. Praça Cívica (Início)
    {"nome": "Av. 85 - Praça Cívica (Sentido Sul)", "lat": "-16.6815", "lon": "-49.2567"}, 
    {"nome": "Av. 85 - Praça Cívica (Sentido Centro)", "lat": "-16.6815", "lon": "-49.2569"},

    # 2. Rua 103
    {"nome": "Av. 85 - Rua 103 (Sentido Sul)", "lat": "-16.6864", "lon": "-49.2594"},  
    {"nome": "Av. 85 - Rua 103 (Sentido Centro)", "lat": "-16.6863", "lon": "-49.2596"},

    # 3. Praça do Ratinho
    {"nome": "Av. 85 - Praça do Ratinho (Sentido Sul)", "lat": "-16.6911", "lon": "-49.2620"}, 
    {"nome": "Av. 85 - Praça do Ratinho (Sentido Centro)", "lat": "-16.6911", "lon": "-49.2622"},

     # 4. Cruzamento Av. T-9 (Marista/Bueno)
    {"nome": "Av. 85 - Av. T-9 (Sentido Sul)", "lat": "-16.6954", "lon": "-49.2640"}, 
    {"nome": "Av. 85 - Av. T-9 (Sentido Centro)", "lat": "-16.6954", "lon": "-49.2642"},

    # 5. Cruzamento Av. Mutirão
    {"nome": "Av. 85 - Mutirão (Sentido Sul)", "lat": "-16.7033", "lon": "-49.2643"},  
    {"nome": "Av. 85 - Mutirão (Sentido Centro)", "lat": "-16.7032", "lon": "-49.2640"}, 

    # 6. Cruzamento Rua T-11
    {"nome": "Av. 85 - Rua T-11 (Sentido Sul)", "lat": "-16.7068", "lon": "-49.2642"},  
    {"nome": "Av. 85 - Rua T-11 (Sentido Centro)", "lat": "-16.7068", "lon": "-49.2639"},

    # 7. Fim da Av. 85 x Edmundo P. de Abreu
    {"nome": "Av. 85 - Final Serrinha (Sentido Sul)", "lat": "-16.7095", "lon": "-49.2640"}, 
    {"nome": "Av. 85 - Final Serrinha (Sentido Centro)", "lat": "-16.7095", "lon": "-49.2638"},
]

def coletar_e_salvar():
    dados = []
    agora = datetime.now().isoformat()

    #Coletando dados da API da TomTom
    for ponto in pontos_monitoramento:
        # Endpoint: Traffic Flow Segment 
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/22/json?point={ponto['lat']},{ponto['lon']}&key={TOMTOM_API_KEY}"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                flow = res.json().get('flowSegmentData', {})
                curr_speed = flow.get('currentSpeed', 0)
                free_speed = flow.get('freeFlowSpeed', 1) 
                
                # Cálculo do Índice de Congestionamento
                ic_index = 1 - (curr_speed / free_speed) if free_speed > 0 else 0
                
                dados.append({
                    "timestamp_coleta": agora,
                    "ponto_nome": ponto['nome'],
                    "latitude": float(ponto['lat']),
                    "longitude": float(ponto['lon']),
                    "current_speed": curr_speed,
                    "free_flow_speed": free_speed,
                    "ic_index": round(ic_index, 3)
                })
        except Exception as e:
            print(f"Erro na coleta do ponto {ponto['nome']}: {e}")

    df = pd.DataFrame(dados)
    
    if not df.empty:
        print("Dados estruturados no Pandas:")
        print(df.head())
        
        registros = df.to_dict(orient='records')
        try:
            resposta = supabase.table("historico_transito").insert(registros).execute()
            print("Inserção concluída com sucesso no banco de dados!")
        except Exception as e:
            print(f"Erro ao inserir registros: {e}")
    else:
        print("Nenhum dado válido foi retornado da API.")

if __name__ == "__main__":
    coletar_e_salvar()