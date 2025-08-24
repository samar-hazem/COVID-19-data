
import pandas as pd

file_path = r"C:\Users\M&R\OneDrive\سطح المكتب\samar.py\بيانات المشروع\covid_2019\COVID-2019 - ECDC (2020).csv"
DataFrame = pd.read_csv(file_path)
print(DataFrame.head())



DataFrame.rename(columns={
    'Total confirmed cases of COVID-19': 'Total_Cases',
    'Total confirmed deaths due to COVID-19': 'Total_Deaths'
}, inplace=True)

# قاموس يربط الدول بالقارات
country_to_continent = {
    'Afghanistan': 'Asia',
    'Germany': 'Europe',
    'Brazil': 'South America',
    'United States': 'North America',
    'China': 'Asia',
    'India': 'Asia',
    'South Africa': 'Africa',
    'Italy': 'Europe',
    'Canada': 'North America',
    'Australia': 'Oceania',
    # أضف باقي الدول حسب الحاجة...
}

# إنشاء عمود جديد للقارة باستخدام القاموس
DataFrame['Continent'] = DataFrame['Country'].map(country_to_continent)


#-----------------------------------------------
# 1-  عالج البيانات المفقودة والمكررة وأخطاء التنسيق

print(DataFrame.isnull().sum())                                                  # طباعة عدد القيم المفقودة في كل عمود

# 1- معالجة البيانات المفقودة بالمتوسط

numeric_cols = DataFrame.select_dtypes(include=['float64', 'int64']).columns     # استدعاء الأعمدة الرقمية فقط

# تعويض القيم المفقودة في الأعمدة الرقمية بالمتوسط الخاص بكل عمود
for col in numeric_cols:
    mean_value = DataFrame[col].mean()
    DataFrame[col] = DataFrame[col].fillna(mean_value)

print("Missing values have been replaced with the mean for all numeric columns.")

# 2- التعامل مع البيانات المكررة

print("Number of duplicated rows:", DataFrame.duplicated().sum())                # التحقق من عدد الصفوف المكررة

DataFrame.drop_duplicates(inplace=True)                                          # حذف الصفوف المكررة (إن وُجدت)
print("Duplicate rows have been removed.")

# 3- معالجة أخطاء التنسيق

DataFrame.columns = DataFrame.columns.str.strip()                                # إزالة الفراغات الزائدة من أسماء الأعمدة

if 'Country' in DataFrame.columns and DataFrame['Country'].dtype == 'object':    # إزالة الفراغات الزائدة من النصوص (مثل أسماء الدول)
    DataFrame['Country'] = DataFrame['Country'].str.strip().str.title()

print("Formatting issues have been resolved.")

#----------------------------------------------------
# حساب بعض المقاييس الرئيسية
# 1- إجمالي الحالات/الوفيات لكل دولة

# حساب إجمالي الحالات لكل دولة
total_cases_per_country = DataFrame.groupby('Country')['Total_Cases'].sum().reset_index().sort_values(by='Total_Cases', ascending=False)

# حساب إجمالي الوفيات لكل دولة
total_deaths_per_country = DataFrame.groupby('Country')['Total_Deaths'].sum().reset_index().sort_values(by='Total_Deaths', ascending=False)

# طباعة أول 10 دول حسب عدد الحالات
print("Top 10 countries by total cases:")
print(total_cases_per_country.head(10))

# طباعة أول 10 دول حسب عدد الوفيات
print("\nTop 10 countries by total deaths:")
print(total_deaths_per_country.head(10))

# 2- معدلات النمو الشهرية

# تحديد تاريخ البداية (1 يناير 2020)
start_date = pd.to_datetime('2020-01-01')

# الى تاريخ فعلي Year تحويل عمود
DataFrame['Date'] = start_date + pd.to_timedelta(DataFrame['Year'], unit='D')

# استخراج الشهر والسنة من التاريخ
DataFrame['Month'] = DataFrame['Date'].dt.to_period('M')

# --------- حساب معدل النمو الشهري للحالات ---------
# تجميع الحالات اليومية لكل دولة داخل كل شهر
monthly_cases = DataFrame.groupby(['Country', 'Month'])['Daily new confirmed cases of COVID-19'].sum().reset_index()

# حساب معدل النمو الشهري للحالات (نسبة التغير)
monthly_cases['Monthly_Growth_Rate'] = monthly_cases.groupby('Country')['Daily new confirmed cases of COVID-19'].pct_change()

# عرض أول النتائج
print(monthly_cases.head(10))

# 3- مقارنة المناطق ( القارات )

DataFrame['Month'] = DataFrame['Date'].dt.to_period('M')

# تجميع عدد الحالات الجديدة شهريًا لكل قارة
continent_monthly = DataFrame.groupby(['Continent', 'Month'])['Daily new confirmed cases of COVID-19'].sum().reset_index()

# حساب معدل النمو الشهري للحالات لكل قارة
continent_monthly['Monthly_Growth_Rate'] = continent_monthly.groupby('Continent')['Daily new confirmed cases of COVID-19'].pct_change()
print(continent_monthly.head(10))

# 4- تحديد الحلات الشاذة

from scipy.stats import zscore
#لكل قارة على حدة لمعدل النمو الشهري Z-score حساب 
continent_monthly['Growth_ZScore'] = continent_monthly.groupby('Continent')['Monthly_Growth_Rate'].transform(zscore)
# أعلى من 2 أو أقل من -2 Z-score : الحلات الشاذة 
outliers = continent_monthly[(continent_monthly['Growth_ZScore'].abs() > 2)]

#  النتائج
print(outliers[['Continent', 'Month', 'Monthly_Growth_Rate', 'Growth_ZScore']])

# --------------------------------------------------
# انشاء بعض الرسومات البيانية
# 1- رسم بياني لسلسلة زمنية للحالات في 3 دول
import matplotlib.pyplot as plt

# اختيار 3 دول لمراقبة تطور الحالات اليومية
selected_countries = ['Italy', 'India', 'Brazil']

# فلترة البيانات للدول المطلوبة
country_ts = DataFrame [DataFrame ['Country'].isin(selected_countries)]

# تجميع البيانات يوميًا
country_ts = country_ts.groupby(['Date', 'Country'])['Daily new confirmed cases of COVID-19'].sum().reset_index()

# الرسم
plt.figure(figsize=(12, 6))
for country in selected_countries:
    subset = country_ts[country_ts['Country'] == country]
    plt.plot(subset['Date'], subset['Daily new confirmed cases of COVID-19'], label=country)

plt.title('Time Series of Daily COVID-19 Cases in Italy, India, and Brazil')
plt.xlabel('Date')
plt.ylabel('Daily New Confirmed Cases')
plt.legend()
plt.tight_layout()
plt.show()

# 2- رسم بيانيي لمعدلات التطعيم مقابل معدلات الوفيات
import pandas as pd
import matplotlib.pyplot as plt

vaccinations = r"C:\Users\M&R\OneDrive\سطح المكتب\samar.py\بيانات المشروع\covid_2019\vaccinations.csv"

# قراءة ملف CSV إلى DataFrame
df = pd.read_csv(vaccinations)
print(df.head())

# 1- تحضير البيانات: نأخذ أحدث سجل لكل دولة

# نرتب حسب التاريخ للحصول على أحدث سجل في الأسفل
df_sorted = df.sort_values(by=['location', 'date'])

# نأخذ آخر سجل لكل دولة (آخر تاريخ)
latest_vacc = df_sorted.groupby('location').tail(1)

# نحتفظ فقط بالأعمدة المهمة
vacc_df = latest_vacc[['location', 'people_fully_vaccinated_per_hundred']]

# 2-  نضيف بيانات الوفيات 

# مثال على إضافة الوفيات يدويًا لبعض الدول
deaths_data = {
    'location': ['Palestine', 'Israel', 'Egypt', 'Jordan', 'Lebanon'],
    'Total_Deaths': [6150, 12500, 24800, 14300, 9500]
}

deaths_df = pd.DataFrame(deaths_data)

# 3- دمج بيانات التطعيم مع الوفيات

merged_df = pd.merge(vacc_df, deaths_df, on='location')

# ترتيب حسب نسبة التطعيم (اختياري)
merged_df = merged_df.sort_values(by='people_fully_vaccinated_per_hundred', ascending=False)

print("\nMerged Data:")
print(merged_df)

# 4- رسم الرسم البياني

# إنشاء الشكل والمحور الأول
fig, ax1 = plt.subplots(figsize=(12, 6))

x = range(len(merged_df))          # عدد الدول
countries = merged_df['location']  # أسماء الدول

# المحور الأول: رسم أعمدة نسبة التطعيم
ax1.bar(x, merged_df['people_fully_vaccinated_per_hundred'], color='skyblue', label='Vaccination Rate (%)')
ax1.set_ylabel('Vaccination Rate (%)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# المحور الثاني: رسم خط الوفيات
ax2 = ax1.twinx()
ax2.plot(x, merged_df['Total_Deaths'], color='red', marker='o', label='Total Deaths')
ax2.set_ylabel('Total Deaths', color='red')
ax2.tick_params(axis='y', labelcolor='red')

plt.xticks(x, countries, rotation=45, ha='right')                   # أسماء الدول على محور X
plt.title('Vaccination Rate vs. Total COVID-19 Deaths by Country')  # عنوان الرسم
fig.tight_layout()
plt.grid(True)
plt.show()

# 3- رسم بياني لخريطة حرارية لبؤر انتشار الحالات عالمية
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

cases_df = pd.read_csv(r"C:\Users\M&R\OneDrive\سطح المكتب\samar.py\بيانات المشروع\covid_2019\owid-covid-data.csv")  

# تجهيز البيانات: نرتب الدول حسب عدد الحالات
top_cases = cases_df[['location', 'total_cases']].sort_values(by='total_cases', ascending=False).head(20)

# إنشاء خريطة حرارية
plt.figure(figsize=(10, 8))
heatmap = sns.heatmap(
    top_cases.set_index('location'),
    annot=True,
    fmt=',',
    cmap='Reds'
)

plt.title("Top 20 Countries by Total COVID-19 Cases")
plt.xlabel("Total Cases")
plt.ylabel("location")
plt.tight_layout()
plt.show()

