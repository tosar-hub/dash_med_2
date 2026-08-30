# requirements.txt
"""
streamlit
pandas
plotly
numpy
"""

# dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Настройка страницы
st.set_page_config(
    page_title="Аналитический дашборд: Заболеваемость в ЦФО",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок
st.title("🏥 Аналитический дашборд по заболеваниям в Центральном федеральном округе")
st.markdown("---")


# --- Генерация демонстрационных данных ---
@st.cache_data
def generate_data():
    """Генерация синтетических данных для демонстрации"""

    regions = [
        "Москва", "Московская область", "Тверская область",
        "Ярославская область", "Владимирская область", "Рязанская область",
        "Смоленская область", "Тульская область", "Калужская область",
        "Брянская область", "Липецкая область", "Орловская область",
        "Курская область", "Белгородская область", "Воронежская область",
        "Тамбовская область", "Ивановская область"
    ]

    diseases = [
        "COVID-19", "Грипп", "ОРВИ", "Пневмония",
        "Сердечно-сосудистые заболевания", "Онкологические заболевания",
        "Диабет", "Гепатит", "Туберкулез", "ВИЧ/СПИД",
        "Заболевания ЖКТ", "Неврологические заболевания"
    ]

    age_groups = ["0-17", "18-40", "41-60", "60+"]
    genders = ["Мужской", "Женский"]

    dates = pd.date_range(start="2023-01-01", end="2026-08-30", freq="D")

    data = []

    for date in dates:
        for region in random.sample(regions, random.randint(5, 10)):
            for disease in random.sample(diseases, random.randint(3, 6)):
                base_cases = random.randint(1, 50)

                # Сезонные колебания
                month = date.month
                if disease in ["Грипп", "ОРВИ"]:
                    seasonal = 1 + 0.7 * np.sin(2 * np.pi * (month - 1) / 12)
                elif disease == "COVID-19":
                    seasonal = 1 + 0.5 * np.sin(2 * np.pi * (month - 3) / 12)
                else:
                    seasonal = 1

                cases = int(base_cases * seasonal * (0.8 + 0.4 * random.random()))

                for age_group in age_groups:
                    age_multiplier = {
                        "0-17": random.uniform(0.3, 1.2),
                        "18-40": random.uniform(0.5, 1.5),
                        "41-60": random.uniform(0.8, 2.0),
                        "60+": random.uniform(1.0, 2.5)
                    }

                    for gender in genders:
                        gender_multiplier = 0.9 if gender == "Женский" else 1.1
                        final_cases = int(cases * age_multiplier[age_group] * gender_multiplier)

                        if final_cases > 0:
                            data.append({
                                "Дата": date,
                                "Регион": region,
                                "Заболевание": disease,
                                "Возрастная группа": age_group,
                                "Пол": gender,
                                "Количество случаев": final_cases,
                                "Госпитализировано": int(final_cases * random.uniform(0.1, 0.4)),
                                "Летальные исходы": int(final_cases * random.uniform(0.01, 0.05))
                            })

    return pd.DataFrame(data)


# Загрузка данных
with st.spinner("Загрузка данных..."):
    df = generate_data()

# --- Боковая панель с фильтрами ---
st.sidebar.header("🔍 Фильтры")

# Выбор периода
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Дата начала",
        value=df["Дата"].min() + timedelta(days=180),
        min_value=df["Дата"].min(),
        max_value=df["Дата"].max()
    )
with col2:
    end_date = st.date_input(
        "Дата окончания",
        value=df["Дата"].max(),
        min_value=df["Дата"].min(),
        max_value=df["Дата"].max()
    )

# Выбор регионов
regions = st.sidebar.multiselect(
    "Выберите регионы",
    options=sorted(df["Регион"].unique()),
    default=sorted(df["Регион"].unique())[:5]
)

# Выбор заболеваний
diseases = st.sidebar.multiselect(
    "Выберите заболевания",
    options=sorted(df["Заболевание"].unique()),
    default=["COVID-19", "Грипп", "ОРВИ", "Пневмония"]
)

# Выбор возрастных групп
age_groups = st.sidebar.multiselect(
    "Возрастные группы",
    options=sorted(df["Возрастная группа"].unique()),
    default=sorted(df["Возрастная группа"].unique())
)

# Выбор пола
genders = st.sidebar.multiselect(
    "Пол",
    options=sorted(df["Пол"].unique()),
    default=sorted(df["Пол"].unique())
)

# Применение фильтров
filtered_df = df[
    (df["Дата"] >= pd.to_datetime(start_date)) &
    (df["Дата"] <= pd.to_datetime(end_date)) &
    (df["Регион"].isin(regions)) &
    (df["Заболевание"].isin(diseases)) &
    (df["Возрастная группа"].isin(age_groups)) &
    (df["Пол"].isin(genders))
    ]

# --- KPI Метрики ---
st.markdown("## 📊 Ключевые показатели")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_cases = filtered_df["Количество случаев"].sum()
    st.metric(
        "Всего случаев",
        f"{total_cases:,}".replace(",", " "),
        delta=f"{int((total_cases / df['Количество случаев'].sum()) * 100)}% от общего числа"
    )

with col2:
    total_hospitalized = filtered_df["Госпитализировано"].sum()
    hospitalization_rate = (total_hospitalized / total_cases * 100) if total_cases > 0 else 0
    st.metric(
        "Госпитализировано",
        f"{total_hospitalized:,}".replace(",", " "),
        delta=f"{hospitalization_rate:.1f}% госпитализации"
    )

with col3:
    total_deaths = filtered_df["Летальные исходы"].sum()
    mortality_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0
    st.metric(
        "Летальные исходы",
        f"{total_deaths:,}".replace(",", " "),
        delta=f"{mortality_rate:.2f}% летальность",
        delta_color="inverse"
    )

with col4:
    avg_daily = total_cases / max(1, len(filtered_df["Дата"].unique()))
    st.metric(
        "Среднесуточная заболеваемость",
        f"{avg_daily:.0f}",
        delta=f"{avg_daily - filtered_df.groupby('Дата')['Количество случаев'].sum().mean():.0f} к среднему"
    )

st.markdown("---")

# --- Графики ---
# Первый ряд: Динамика заболеваемости и распределение по регионам
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Динамика заболеваемости")

    daily_cases = filtered_df.groupby("Дата")["Количество случаев"].sum().reset_index()

    fig1 = px.line(
        daily_cases,
        x="Дата",
        y="Количество случаев",
        title="Ежедневная заболеваемость",
        template="plotly_white",
        labels={"Количество случаев": "Число случаев", "Дата": "Дата"}
    )
    fig1.update_traces(line=dict(color="#1f77b4", width=2))
    fig1.add_hline(
        y=daily_cases["Количество случаев"].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Среднее: {daily_cases['Количество случаев'].mean():.0f}"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🏥 Распределение по регионам")

    region_cases = filtered_df.groupby("Регион")["Количество случаев"].sum().sort_values(ascending=True).tail(10)

    fig2 = px.bar(
        region_cases,
        x=region_cases.values,
        y=region_cases.index,
        orientation="h",
        title="Топ-10 регионов",
        template="plotly_white",
        labels={"x": "Число случаев", "y": "Регион"},
        color=region_cases.values,
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Второй ряд: Распределение по заболеваниям и возрастным группам
col1, col2 = st.columns(2)

with col1:
    st.subheader("🦠 Заболеваемость по типам")

    disease_cases = filtered_df.groupby("Заболевание")["Количество случаев"].sum().sort_values(ascending=True)

    fig3 = px.bar(
        disease_cases,
        x=disease_cases.values,
        y=disease_cases.index,
        orientation="h",
        title="Распределение по заболеваниям",
        template="plotly_white",
        labels={"x": "Число случаев", "y": "Заболевание"},
        color=disease_cases.values,
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("👤 Распределение по возрастным группам")

    age_cases = filtered_df.groupby("Возрастная группа")["Количество случаев"].sum()

    fig4 = px.pie(
        age_cases,
        values=age_cases.values,
        names=age_cases.index,
        title="Доля по возрастным группам",
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig4.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig4, use_container_width=True)

# Третий ряд: Тепловая карта и дополнительный анализ
st.markdown("---")
st.subheader("🌡️ Детальный анализ")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Гендерное распределение")
    gender_cases = filtered_df.groupby("Пол")["Количество случаев"].sum()

    fig5 = px.pie(
        gender_cases,
        values=gender_cases.values,
        names=gender_cases.index,
        template="plotly_white",
        color_discrete_sequence=["#3498db", "#e74c3c"]
    )
    fig5.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.markdown("#### Госпитализация по заболеваниям")

    disease_hospital = filtered_df.groupby("Заболевание")[["Количество случаев", "Госпитализировано"]].sum()
    disease_hospital["% госпитализации"] = (
                disease_hospital["Госпитализировано"] / disease_hospital["Количество случаев"] * 100).round(1)
    disease_hospital = disease_hospital.sort_values("% госпитализации", ascending=False).head(8)

    fig6 = px.bar(
        disease_hospital,
        x=disease_hospital.index,
        y="% госпитализации",
        title="% госпитализации по заболеваниям",
        template="plotly_white",
        labels={"x": "Заболевание", "% госпитализации": "%"},
        color="% госпитализации",
        color_continuous_scale="Oranges"
    )
    st.plotly_chart(fig6, use_container_width=True)

with col3:
    st.markdown("#### Летальность по возрастным группам")

    age_mortality = filtered_df.groupby("Возрастная группа")[["Количество случаев", "Летальные исходы"]].sum()
    age_mortality["% летальности"] = (
                age_mortality["Летальные исходы"] / age_mortality["Количество случаев"] * 100).round(2)

    fig7 = px.bar(
        age_mortality,
        x=age_mortality.index,
        y="% летальности",
        title="Летальность по возрастным группам",
        template="plotly_white",
        labels={"x": "Возрастная группа", "% летальности": "%"},
        color="% летальности",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig7, use_container_width=True)

# --- Дополнительная информация ---
st.markdown("---")
st.markdown("### 📋 Сводная статистика")

# Сводная таблица
summary_df = filtered_df.groupby(["Регион", "Заболевание"]).agg({
    "Количество случаев": "sum",
    "Госпитализировано": "sum",
    "Летальные исходы": "sum"
}).reset_index()

summary_df["% госпитализации"] = (summary_df["Госпитализировано"] / summary_df["Количество случаев"] * 100).round(1)
summary_df["% летальности"] = (summary_df["Летальные исходы"] / summary_df["Количество случаев"] * 100).round(2)

# Выбор региона для детализации
selected_region_for_detail = st.selectbox(
    "Выберите регион для детальной статистики",
    options=sorted(regions)
)

if selected_region_for_detail:
    region_detail = summary_df[summary_df["Регион"] == selected_region_for_detail]

    # Три колонки для детальной статистики
    c1, c2, c3 = st.columns(3)

    with c1:
        total = region_detail["Количество случаев"].sum()
        st.metric(f"Всего случаев в {selected_region_for_detail}", f"{total:,}".replace(",", " "))

    with c2:
        hosp = region_detail["Госпитализировано"].sum()
        hosp_pct = (hosp / total * 100) if total > 0 else 0
        st.metric("Госпитализировано", f"{hosp:,}".replace(",", " "), f"{hosp_pct:.1f}%")

    with c3:
        deaths = region_detail["Летальные исходы"].sum()
        death_pct = (deaths / total * 100) if total > 0 else 0
        st.metric("Летальные исходы", f"{deaths:,}".replace(",", " "), f"{death_pct:.2f}%")

    # Таблица с деталями
    st.dataframe(
        region_detail.sort_values("Количество случаев", ascending=False),
        column_config={
            "Количество случаев": st.column_config.NumberColumn("Случаи", format="%d"),
            "Госпитализировано": st.column_config.NumberColumn("Госпитализировано", format="%d"),
            "Летальные исходы": st.column_config.NumberColumn("Летальные исходы", format="%d"),
            "% госпитализации": st.column_config.NumberColumn("% госпитализации", format="%.1f%%"),
            "% летальности": st.column_config.NumberColumn("% летальности", format="%.2f%%")
        },
        use_container_width=True,
        hide_index=True
    )

# Экспорт данных
st.markdown("---")
st.markdown("### 📥 Экспорт данных")

if st.button("Скачать данные в CSV"):
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Скачать CSV",
        data=csv,
        file_name=f"заболеваемость_цфо_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption(f"📅 Данные актуальны на {datetime.now().strftime('%d.%m.%Y %H:%M')}")
st.caption(f"📊 Всего записей: {len(filtered_df):,}")