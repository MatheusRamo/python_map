from flask import Flask, render_template_string
import pandas as pd
import folium

app = Flask(__name__)


@app.route("/")
def components():

    df = pd.read_csv('dados_prismas.csv')
    # Converta a coluna 'Data' para o tipo de data
    df['Data'] = pd.to_datetime(df['Data'],  format='%d/%m/%Y')
    print(df['Data'])
    df = df.sort_values('Data')

    # Crie um mapa centrado na média de suas coordenadas
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=17, tiles = None)
    folium.TileLayer(tiles = "cartodbpositron").add_to(m)
    folium.TileLayer(tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                    name = "Imagem Satélite").add_to(m)

    folium.LayerControl().add_to(m)

    datas_unicas = []
    for data in df['Data'].unique():
        datas_unicas.append(data.date())

    
    
    # html = '<div class="container"> <div class="mapa-pequeno"> mapa pequeno </div> <div class="mapa-grande">'

    # Adicione um marcador para cada prisma
    for prisma in df['Prisma'].unique():
        df_prisma = df[df['Prisma'] == prisma]

        # Use a última localização disponível para o marcador
        location = df_prisma.iloc[-1][['Latitude', 'Longitude']]

        html = '<h3>' + prisma + '</h3>'
        for i, row in df_prisma.iterrows():
            html += f"""
            <h4> Data:  { str(row['Data'].date())} </h4>
            <ul>
                <li><b>N:</b> {str(round(row['Norte'], 5))} </li>
                <li><b>E:</b> {str(round(row['Leste'], 5))}  </li>
                <li><b>Elevação:</b> {str(round(row['Elevacao'], 5))} </li>
            </ul>
            """
        iframe = folium.IFrame(html=html, width=400, height=400)
        popup = folium.Popup(iframe, max_width=400)
        # Adicione o marcador ao mapa
        folium.Marker(location, popup=popup).add_to(m)
    
    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                <style>
                    body, html {
                        margin: 0;
                        padding: 0;
                        height: 100%;
                        width: 100%;
                    }
                    .container {
                        display: flex;
                        height: 100vh;
                        width: 100vw;
                    }
                    .mapa-grande {
                        flex: 70%;
                        background-size: cover;
                    }
                    .mapa-pequeno {
                        flex: 30%;
                        background-size: cover;
                    }
                </style>
                    {{ header|safe }}
                </head>
                <body>
                    <h1>Campo Grande</h1>
                   
                       {{ body_html|safe }}

                    
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script,
    )


if __name__ == "__main__":
    app.run(debug=True)