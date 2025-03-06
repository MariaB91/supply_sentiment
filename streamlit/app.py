def show_dashboard():
    st.title("📊 Dashboard d'Analyse des Avis Clients")
    
    df, trust_scores, marque_to_company = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    marque = st.sidebar.selectbox("Sélectionner une marque", options=list(marque_to_company.keys()))
    company_name = marque_to_company.get(marque, "")
    df = df[df['company_name'] == company_name]
    trust_score = trust_scores.get(company_name, 0.0)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

    today = datetime.now()
    start_6m = today - timedelta(days=180)

    df_6m = df[df['review_date'] >= start_6m]

    # Ajouter une colonne pour savoir s'il y a une réponse ou non
    df_6m['has_response'] = df_6m['response'].notna()

    # Regrouper les avis par mois
    df_6m['month'] = df_6m['review_date'].dt.to_period('M')  # Extraire l'année et le mois
    df_6m['month'] = df_6m['month'].astype(str)  # Assurer que 'month' est en format string

    # Évolution des notes par mois (moyenne des notes)
    df_trend_6m = df_6m.groupby(df_6m['month'])['rating'].mean().reset_index()

    # Vérification des valeurs manquantes et suppression si nécessaire
    df_trend_6m = df_trend_6m.dropna(subset=['rating', 'month'])  # Supprimer les lignes avec des valeurs manquantes

    col1, col2 = st.columns(2)

    # Évolution des notes
    with col1:
        fig_6m = px.line(df_trend_6m, x='month', y='rating', title="Évolution des Notes (6 Mois)", markers=True, 
                         line_shape='linear', title_x=0.5)
        fig_6m.update_xaxes(title="Mois", showgrid=True, gridcolor='lightgray')
        fig_6m.update_yaxes(title="Note Moyenne", showgrid=True, gridcolor='lightgray')
        fig_6m.update_traces(line=dict(color='royalblue'))
        st.plotly_chart(fig_6m, use_container_width=True)

    # Distribution des notes
    with col2:
        fig_dist = px.histogram(df_6m, x='rating', nbins=5, title="Distribution des Notes", labels={'rating': 'Notes'}, 
                                title_x=0.5, color_discrete_sequence=['royalblue'])
        fig_dist.update_xaxes(title="Notes (1-5)", showgrid=True, gridcolor='lightgray')
        fig_dist.update_yaxes(title="Nombre d'Avis", showgrid=True, gridcolor='lightgray')
        st.plotly_chart(fig_dist, use_container_width=True)

    # Répartition globale des réponses et non-réponses
    responses_count = df_6m['has_response'].sum()
    no_responses_count = len(df_6m) - responses_count

    # Création du graphique pie chart global (réponses vs non-réponses)
    labels = ['Réponses', 'Non-réponses']
    sizes = [responses_count, no_responses_count]
    colors = ['#A1D6E2', '#FFB2A6']
    explode = (0.1, 0)  # Mettre en évidence le premier segment

    fig_pie_global = go.Figure(go.Pie(labels=labels, values=sizes, hole=0.3, marker=dict(colors=colors), textinfo='percent+label'))
    fig_pie_global.update_layout(title="Répartition Globale des Réponses et Non-Réponses", title_x=0.5, height=400)
    st.plotly_chart(fig_pie_global, use_container_width=True)

    # Répartition des réponses par mois
    df_responses_by_month = df_6m.groupby(['month', 'has_response']).size().unstack(fill_value=0)
    
    # Ajouter des colonnes 'Réponses' et 'Non-réponses' explicitement
    df_responses_by_month['Réponses'] = df_responses_by_month[True]  # Réponses
    df_responses_by_month['Non-réponses'] = df_responses_by_month[False]  # Non-réponses

    # Création du graphique pour chaque mois avec pie chart
    fig_pie_month = go.Figure()

    # Ajouter une trace pour chaque mois
    for month, data in df_responses_by_month.iterrows():
        fig_pie_month.add_trace(go.Pie(
            labels=['Réponses', 'Non-réponses'],
            values=[data['Réponses'], data['Non-réponses']],
            name=str(month),
            hole=0.3,
            marker=dict(colors=colors)
        ))

    fig_pie_month.update_layout(
        title="Répartition des Réponses par Mois",
        title_x=0.5,
        height=500,
        grid=dict(rows=3, columns=2),
        showlegend=False
    )
    st.plotly_chart(fig_pie_month, use_container_width=True)

if __name__ == "__main__":
    show_dashboard()
