import marimo

__generated_with = "0.11.0"
app = marimo.App(width="full")


@app.cell
def _():
    import polars as pl
    import marimo as mo
    import pandas as pd
    import altair as alt
    return alt, mo, pd, pl


@app.cell
def _(pl):
    df = pl.read_csv("shopping_trends.csv")
    df
    return (df,)


@app.cell
def _(mo):
    mo.md(
        r"""
        ### 📌 **Análises Estatísticas e Insights**
        1. **Análise Demográfica:** Qual é a média de idade dos clientes? Existe diferença na faixa etária entre homens e mulheres?
        2. **Categorias de Produtos:** Qual categoria de produto tem mais vendas? E qual gera mais receita?
        3. **Distribuição de Avaliações:** Qual é a média de avaliação dos produtos comprados? Algum fator influencia uma melhor avaliação?
        4. **Descontos x Compras:** Clientes que usaram desconto gastam mais ou menos em média do que os que não usaram?
        """
    )
    return


@app.cell
def _(df):
    # Média de idade dos Clientes
    avg_age = sum(df['Age']) / df['Customer ID'].n_unique()
    print(f"Média de Idade: {avg_age:.2f}")
    return (avg_age,)


@app.cell
def _(df, pl):
    # Diferença na faixa etária entre sexos (M/F)
    df_filtered = df.select(["Gender", "Age"])
    age_summary = df_filtered.group_by("Gender").agg(pl.col("Age").mean().round(2).alias("Average Age Per Sex"))
    age_summary
    return age_summary, df_filtered


@app.cell
def _(df, pl):
    # Season que mais vende
    season_most_sale = df.select(["Season", "Purchase Amount (USD)"])
    season = season_most_sale.group_by("Season").agg(pl.col("Purchase Amount (USD)").sum().round(2))
    season
    return season, season_most_sale


@app.cell
def _(df):
    # Calculo de vendas por season
    season_filtered = df.filter(df["Season"] == "Summer")
    season_sales = season_filtered["Purchase Amount (USD)"].sum()
    season_sales 
    return season_filtered, season_sales


@app.cell
def _(df):
    # Qual categoria de produto tem mais vendas?
    category_sales = df.group_by("Category").len()
    category_sales
    return (category_sales,)


@app.cell
def _(df, pl):
    # E qual gera mais receita?
    category_most_sales = df.group_by("Category").agg(pl.col("Purchase Amount (USD)").sum().alias("Category Most Sales"))
    category_most_sales
    return (category_most_sales,)


@app.cell
def _(df):
    # Verificar se a conta de vendas por categoria está correta
    clothing = df.filter(df["Category"] == "Clothing")
    clothing_sales = clothing["Purchase Amount (USD)"].sum()
    clothing_sales
    return clothing, clothing_sales


@app.cell
def _(df):
    # Soma total das vendas
    total_sales = df.select([df["Purchase Amount (USD)"].sum()])
    total_sales
    return (total_sales,)


@app.cell
def _(df):
    # Qual é a média de avaliação dos produtos comprados?
    AVG_Rating = df["Review Rating"].mean()
    print(f"Média de avaliação: {AVG_Rating:.2f}")
    return (AVG_Rating,)


@app.cell
def _(df, pl):
    # Correlação entre "Review Rating" e outras colunas numéricas

    # Verifica quais colunas são numéricas
    numeric_columns = df.select(pl.col(pl.Float64, pl.Int64)).columns

    # Calcula a correlação de "Rating" com as outras colunas numéricas
    correlation = df.select([pl.corr("Review Rating", col).round(2).alias(f"Corr_Rating_{col}") for col in numeric_columns if col != "Review Rating"])

    correlation
    return correlation, numeric_columns


@app.cell
def _(df, pl):
    # Avaliação por Faixa Etária e Gênero
    age_gender_rating = df.group_by(["Age", "Gender", "Category"]).agg(pl.col("Review Rating").mean().round(2))

    age_gender_rating
    return (age_gender_rating,)


@app.cell
def _(mo):
    mo.md(
        r"""
        ### 📊 **Visualização de Dados**
        5. **Gráfico de compras por categoria:** Um gráfico de barras mostrando quais categorias vendem mais.
        6. **Mapa de calor de compras por localização:** Onde estão os clientes que mais compram?
        7. **Histograma da idade dos compradores:** Existe um grupo etário que mais compra?
        8. **Boxplot do valor de compras:** Qual a distribuição do valor gasto pelos clientes?
        """
    )
    return


@app.cell
def _(alt, category_sales, mo):
    # Gráfico de barras mostrando quais categorias vendem mais
    category_sales_pandas = category_sales.to_pandas()
    print(category_sales_pandas.columns)
    # Deve exibir algo como: Index(['Category', 'Category Most Sales'], dtype='object')

    chart = alt.Chart(category_sales_pandas).mark_bar().encode(
        x=alt.X('Category:N', title='Categoria'),
        y=alt.Y('len:Q', title='Total de Vendas (USD)'),
        color="Category"
    )

    chart = mo.ui.altair_chart(chart)
    chart
    return category_sales_pandas, chart


@app.cell
def _(df, pl):
    # Onde estão os clientes que mais compram?
    state_sales = (df.group_by("Location").agg(pl.col("Purchase Amount (USD)").len()).rename({"Location": "state", "Purchase Amount (USD)": "sales"}))
    state_sales["state", "sales"]
    return (state_sales,)


@app.cell
def _(alt, state_sales):
    # Carregar o TopoJSON dos estados dos EUA
    # Usaremos a propriedade 'states' do arquivo JSON
    us_states = alt.topo_feature("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json", "states")


    chart_state_sales = alt.Chart(us_states).mark_geoshape().encode(
        # O lookup faz a junção dos dados de vendas com o TopoJSON,
        # usando a propriedade "name" do topojson e a coluna "state" dos dados.
        color=alt.Color("sales:Q",
                        scale=alt.Scale(scheme="blues"),
                        title="Total de Vendas (USD)"),
        tooltip=[
            alt.Tooltip("properties.name:N", title="Estado"),
            alt.Tooltip("sales:Q", title="Total de Vendas", format=",.2f")
        ]
    ).transform_lookup(
        lookup="properties.name",  # A propriedade do TopoJSON que contém o nome do estado
        from_=alt.LookupData(state_sales, "state", ["sales"])
    ).project(
        type="albersUsa"
    ).properties(
        width=800,
        height=500,
        title="Mapa de Vendas por Estado"
    )
    chart_state_sales
    return chart_state_sales, us_states


@app.cell
def _(df, pl):
    # Existe um grupo etário que mais compra?
    group_age_most_buy = df.group_by(["Age", "Gender"]).agg(pl.col("Previous Purchases").sum())
    group_age_most_buy

    return (group_age_most_buy,)


@app.cell
def _(alt, group_age_most_buy, mo):
    # Supondo que group_age_most_buy é um DataFrame do Polars
    group_age_most_buy_pd = group_age_most_buy.to_pandas()

    # Padroniza a coluna Gender (remove espaços e formata)
    group_age_most_buy_pd['Gender'] = (
        group_age_most_buy_pd['Gender']
        .str.strip()  # Remove espaços extras
        .str.title()  # Converte para "Female" e "Male"
    )

    # Cria o gráfico
    chart_group_sales = alt.Chart(group_age_most_buy_pd).mark_bar().encode(
        x=alt.X('Age:O', title='Idade'),
        y=alt.Y('Previous Purchases:Q', title='Total de Compras'),
        color=alt.Color('Gender:N', title='Gênero', scale=alt.Scale(scheme='set1')),
        column=alt.Column('Gender:N', title='')
    ).properties(
        title='Total de Compras por Idade e Gênero',
        width=800
    )
    chart_group_sales = mo.ui.altair_chart(chart_group_sales)
    chart_group_sales
    return chart_group_sales, group_age_most_buy_pd


@app.cell
def _(alt, df, mo):
    # Qual a distribuição do valor gasto pelos clientes? BOXPLOT
    boxplot = df.select(["Purchase Amount (USD)", "Age"])
    boxplot

    boxplot_pd = boxplot.to_pandas()

    print(boxplot_pd.columns)

    boxplot_chart = alt.Chart(boxplot_pd).mark_boxplot(extent='min-max').encode(
        x='Age:O',
        y='Purchase Amount (USD):Q'
    )

    boxplot_chart = mo.ui.altair_chart(boxplot_chart)

    boxplot_chart
    return boxplot, boxplot_chart, boxplot_pd


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
