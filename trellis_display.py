
# Import thư viện
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Đọc dữ liệu
hr = pd.read_csv("hr.csv")

# Xem nhanh vài dòng đầu
print(hr.head())


plt.figure(figsize=(8, 5))
sns.boxplot(x="Department", y="MonthlyIncome", hue="Attrition", data=hr)
plt.title("Monthly Income by Department and Attrition")
plt.xlabel("Department")
plt.ylabel("Monthly Income")
plt.legend(title="Attrition")
plt.tight_layout()
plt.show()

########################################################################

#########################################################################

# Thiết lập style
sns.set(style="whitegrid")

# Tạo Trellis (FacetGrid)
g = sns.FacetGrid(hr, col="Department", row="OverTime", hue="Attrition", height=3.5)
g.map_dataframe(sns.scatterplot, x="YearsAtCompany", y="MonthlyIncome", alpha=0.7)

# Thêm tiêu đề và định dạng
g.add_legend()
g.set_axis_labels("Years at Company", "Monthly Income")
g.fig.subplots_adjust(top=0.9)
g.fig.suptitle("Trellis Display: Monthly Income vs Years at Company\nFaceted by Department and OverTime")

plt.show()

#########################################################################
min_y = int(np.floor(hr['YearsAtCompany'].min()))
max_y = int(np.ceil(hr['YearsAtCompany'].max()))

# --- Tạo shingles (cửa sổ chồng lấp) ---
# Danh sách các start point cho cửa sổ: từ min_y đến max_y - window_size, bước 'step'
window_size = 3              # kích thước cửa sổ (năm) - ví dụ 3 năm
step = 1                     # bước di chuyển (năm) - ví dụ 1 năm
max_cols = 6                  # tối đa số cột (panel) bạn muốn hiển thị ngang; tăng/giảm nếu cần

starts = list(range(min_y, max_y - window_size + 1, step))

# Nếu quá nhiều panel, cắt bớt (giữ các cửa sổ ở giữa hoặc theo yêu cầu)
if len(starts) > max_cols:
    # giữ các cửa sổ ở giữa để không tạo quá nhiều panel
    center = len(starts) // 2
    half = max_cols // 2
    start_index = max(0, center - half)
    starts = starts[start_index:start_index + max_cols]

# Chuẩn bị dataframe mở rộng: mỗi record có thể xuất hiện trong nhiều cửa sổ
rows = []
for s in starts:
    e = s + window_size
    label = f"{s}–{e}"   # nhãn panel
    mask = (hr['YearsAtCompany'] >= s) & (hr['YearsAtCompany'] <= e)
    subset = hr.loc[mask].copy()
    if subset.empty:
        continue
    subset['shingle'] = label
    subset['shingle_start'] = s
    subset['shingle_end'] = e
    rows.append(subset)

if not rows:
    raise SystemExit("Không có dữ liệu rơi vào bất kỳ cửa sổ shingle nào. Kiểm tra window_size / dữ liệu.")

shingle_df = pd.concat(rows, ignore_index=True)

# Đổi shingle thành category có order theo start để plot đúng thứ tự
order = sorted(shingle_df['shingle'].unique(), key=lambda x: int(x.split('–')[0]))
shingle_df['shingle'] = pd.Categorical(shingle_df['shingle'], categories=order, ordered=True)

# --- Vẽ shingle trellis ---
sns.set(style="whitegrid")
# Tạo FacetGrid: hàng = Department, cột = shingle (cửa sổ YearsAtCompany)
# Nếu muốn row = OverTime và col = shingle, hoán đổi row/col
g = sns.relplot(
    data=shingle_df,
    x="YearsAtCompany",
    y="MonthlyIncome",
    col="shingle",
    row="Department",
    hue="Attrition",
    kind="scatter",
    height=3,
    aspect=1,
    facet_kws={'sharey': True, 'sharex': True},
    alpha=0.7,
    palette="tab10"
)

g.fig.subplots_adjust(top=0.92)
g.fig.suptitle("Shingle Trellis: Monthly Income vs YearsAtCompany (sliding windows)", fontsize=14)

# Tinh chỉnh nhãn cho đẹp
for ax in g.axes.flatten():
    if ax is None:
        continue
    ax.set_xlabel("YearsAtCompany")
    ax.set_ylabel("MonthlyIncome")

# Nếu có nhiều cột quá nhỏ, xoay xticks
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()




#########################################################################

# Trellis quá phức tạp (4 phân loại + 4 liên tục)
sns.set(style="whitegrid")

g = sns.relplot(
    data=hr,
    x="YearsAtCompany",
    y="MonthlyIncome",
    col="Department",
    row="OverTime",
    hue="Attrition",
    size="WorkLifeBalance",
    style="JobSatisfaction",
    kind="scatter",
    height=3,
    alpha=0.7,
    palette="tab10"
)

g.fig.subplots_adjust(top=0.9)
g.fig.suptitle("Overloaded Trellis Display: Too Many Dimensions")
plt.show()
