import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==================== 1. 页面整体配置 ====================
st.set_page_config(
    page_title="胡思乱想小工具", 
    layout="wide", 
    page_icon="💡"
)

# 中文字体设置（适配绘图）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 2. 核心模型类 (HSM) ====================
class HousingSovereigntyModel:
    def __init__(self, total_cash, house_price, down_payment, car_cost,
                 loan_rate_year, loan_years, invest_rate_year, rent_market, monthly_savings):
        self.A = total_cash
        self.house_price = house_price
        self.P_down = down_payment
        self.P_car = car_cost
        self.L = house_price - down_payment
        self.i_loan = loan_rate_year / 100 / 12
        self.n = loan_years * 12
        self.i_invest = invest_rate_year / 100 / 12
        self.R_rent = rent_market
        self.S_save = monthly_savings

    def calculate(self):
        if self.i_loan == 0:
            self.M = self.L / self.n
        else:
            self.M = self.L * self.i_loan * (1 + self.i_loan) ** self.n / ((1 + self.i_loan) ** self.n - 1)

        self.cash_locked = self.P_down + self.P_car
        self.cash_remaining = self.A - self.cash_locked
        self.income_total = self.A * self.i_invest
        self.income_remaining = self.cash_remaining * self.i_invest

        self.net_cost_buy = self.M - self.income_remaining
        self.net_cost_rent = self.R_rent - self.income_total

        self.delta_p = self.net_cost_buy - self.net_cost_rent
        self.safety_margin = self.S_save - self.M
        self.simulate_30_years()

    def simulate_30_years(self):
        balance_buy = self.cash_remaining
        balance_rent = self.A
        for _ in range(self.n):
            balance_buy = balance_buy * (1 + self.i_invest) + self.S_save - self.M
            balance_rent = balance_rent * (1 + self.i_invest) + self.S_save - self.R_rent
        self.final_balance_buy = balance_buy
        self.final_balance_rent = balance_rent
        self.wealth_diff = balance_buy - balance_rent

# ==================== 3. 侧边栏导航 ====================
st.sidebar.title("🧰 胡思乱想工具箱")
st.sidebar.markdown("一名 00 后研究生的理智与胡思乱想")

# 定义菜单选项
tool_choice = st.sidebar.radio(
    "请选择小工具：",
    ["🏠 住房主权量化器", "🎓 论文压力计算器"]
)

st.sidebar.divider()
st.sidebar.caption("💡 提示：所有计算仅供逻辑参考，数据不替你做决策。")

# ==================== 4. 逻辑分发 ====================

# --- 工具 1：住房主权量化器 ---
if tool_choice == "🏠 住房主权量化器":
    st.title("🏠 住房主权量化模型 HSM v3.0")

    with st.expander("📌 点击展开：为什么我们需要这款量化模型？", expanded=True):
        st.markdown("""
        购房对年轻人的压力由来已久，大家受这苦很久了。
        所以我决定要做这个模型，去衡量买房比租房多支出而得到的“房产主权”的价格。
        只要你心里觉得，每个月多付这笔钱去买这份主权是划算的，那就买；不然就是租房划算。
        """)

    # 侧边栏参数（仅在当前工具下显示）
    st.sidebar.header("📋 HSM 参数配置")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        total_cash = st.number_input("初始现金(万)", value=90.0) * 10000
        down_payment = st.number_input("首付(万)", value=52.5) * 10000
        car_cost = st.number_input("购车款(万)", value=25.0) * 10000
        loan_years = st.number_input("贷款年限", value=30)
    with col2:
        house_price = st.number_input("房屋总价(万)", value=175.0) * 10000
        loan_rate = st.number_input("房贷利率(%)", value=2.6, step=0.1)
        invest_rate = st.number_input("理财年化(%)", value=3.0, step=0.1)
        rent = st.number_input("月租金(元)", value=4000)
        savings = st.number_input("月攒钱(元)", value=15000)

    if st.sidebar.button("🚀 开始量化主权", type="primary"):
        if down_payment + car_cost > total_cash:
            st.error("❌ 现金流预警：首付+购车款超过了你的初始现金。")
        else:
            model = HousingSovereigntyModel(total_cash, house_price, down_payment, car_cost,
                                            loan_rate, int(loan_years), invest_rate, rent, savings)
            model.calculate()
            st.session_state.model = model
            st.session_state.calculated = True

    # 结果展示
    if st.session_state.get('calculated'):
        m = st.session_state.model
        st.subheader("📊 核心量化指标")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("房产主权价格", f"{m.delta_p:,.0f} 元/月")
        c2.metric("安全边际", f"{m.safety_margin:,.0f} 元/月")
        c3.metric("30年财富差", f"{m.wealth_diff/10000:,.1f} 万")
        c4.metric("30年主权代价", f"{m.delta_p * 12 * 30 / 300000:.1f} 台XT5")
        
        st.info("💡 只要你认为这笔钱买到的“归属感”超过了金额本身，买房就是理性的。")
        chart_data = pd.DataFrame({
            "方案": ["买房(现金)", "纯租房(现金)"],
            "期末资产(万)": [m.final_balance_buy / 10000, m.final_balance_rent / 10000]
        })
        st.bar_chart(chart_data, x="方案", y="期末资产(万)")

# --- 工具 2：论文压力计算器 ---
elif tool_choice == "🎓 论文压力计算器":
    st.title("🎓 论文写作压力对冲模型")
    st.markdown("---")
    st.subheader("研一 J 人专属：为学术焦虑建模")
    st.image("https://via.placeholder.com/800x400.png?text=Model+Under+Construction", caption="模型正在构建中...")
    
    st.info("""
    **正在接入以下变量：**
    * 距离 Deadline 的倒计时天数
    * 导师回复消息的平均延迟 (h)
    * 每天有效阅读文献的时间 (min)
    * 昨晚的深度睡眠时长 (h)
    
    我们将通过数据告诉你：你是真的该焦虑了，还是该关掉电脑去睡一觉。
    """)
    st.warning("预计 v4.0 版本正式上线，敬请期待。")
