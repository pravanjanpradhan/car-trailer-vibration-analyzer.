
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.integrate import solve_ivp

# ------------------------------------------------------------
# ME4131 | Car-Trailer Two-DOF Vibration Analyzer
# ------------------------------------------------------------
st.set_page_config(
    page_title="Car-Trailer Two-DOF Vibration Analyzer",
    page_icon="⚙️",
    layout="wide",
)

LOGO_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/8/80/"
    "NIT_Rourkela_Colour_Logo_Official.png"
)

st.markdown("""
<style>
    .main-title {font-size: 1.55rem; font-weight: 750; margin-bottom: 0.15rem;}
    .sub-title {font-size: 1.0rem; color: #64748b; margin-top: 0;}
    .metric-card {padding: 0.7rem 0.9rem; border: 1px solid rgba(128,128,128,.28);
                  border-radius: 0.7rem;}
    div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.22);
        padding: 0.7rem; border-radius: 0.65rem;}
</style>
""", unsafe_allow_html=True)

# Mandatory assignment header
head_left, head_right = st.columns([1, 6], vertical_alignment="center")
with head_left:
    try:
        st.image(LOGO_URL, width=105)
    except Exception:
        st.markdown("### NITR")
with head_right:
    st.markdown("### NATIONAL INSTITUTE OF TECHNOLOGY ROURKELA")
    st.markdown("**Subject Code:** ME4131 &nbsp;&nbsp; | &nbsp;&nbsp; **Subject Name:** Mechanical Vibration")
    st.markdown("**Application:** Car-Trailer Two-DOF Vibration Analyzer")
st.divider()

st.markdown('<div class="main-title">Interactive Free Vibration Analysis</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">A two-degree-of-freedom, free-free car–trailer system '
    'connected by a linear hitch spring.</div>', unsafe_allow_html=True
)

# Sidebar inputs
st.sidebar.header("System Parameters")
st.sidebar.caption("Change the values to update the analysis instantly.")
M = st.sidebar.number_input("Car mass, M (kg)", min_value=1.0, max_value=100000.0,
                            value=2000.0, step=100.0)
m = st.sidebar.number_input("Trailer mass, m (kg)", min_value=1.0, max_value=100000.0,
                            value=1000.0, step=100.0)
k_kn = st.sidebar.number_input("Hitch stiffness, k (kN/m)", min_value=0.01,
                               max_value=100000.0, value=180.0, step=10.0)
k = k_kn * 1000.0

st.sidebar.header("Initial Conditions")
st.sidebar.caption("Used for the time-response simulation. Positive displacement is to the right.")
x10_mm = st.sidebar.number_input("Initial car displacement, x1(0) (mm)",
                                 value=10.0, step=1.0)
x20_mm = st.sidebar.number_input("Initial trailer displacement, x2(0) (mm)",
                                 value=0.0, step=1.0)
v10_mms = st.sidebar.number_input("Initial car velocity, v1(0) (mm/s)",
                                  value=0.0, step=1.0)
v20_mms = st.sidebar.number_input("Initial trailer velocity, v2(0) (mm/s)",
                                  value=0.0, step=1.0)
duration = st.sidebar.slider("Simulation duration (s)", min_value=1.0, max_value=20.0,
                             value=5.0, step=0.5)

# Matrices and exact analytical eigen-results
Mmat = np.array([[M, 0.0], [0.0, m]], dtype=float)
Kmat = np.array([[k, -k], [-k, k]], dtype=float)
omega_rigid = 0.0
omega_elastic = np.sqrt(k * (1.0 / M + 1.0 / m))
freq_elastic = omega_elastic / (2.0 * np.pi)
period_elastic = 1.0 / freq_elastic
mu = M * m / (M + m)

# Modes: arbitrary unnormalised modes, and mass-normalised modes
modes = np.array([[1.0, 1.0], [1.0, -M / m]], dtype=float).T
# columns are [1,1] and [1,-M/m]
mass_norm_modes = np.zeros_like(modes)
for j in range(2):
    modal_mass = modes[:, j].T @ Mmat @ modes[:, j]
    mass_norm_modes[:, j] = modes[:, j] / np.sqrt(modal_mass)

# Top-level result cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rigid-body frequency", "0.000 Hz")
c2.metric("Elastic natural frequency", f"{freq_elastic:.4f} Hz")
c3.metric("Circular natural frequency", f"{omega_elastic:.4f} rad/s")
c4.metric("Elastic-mode period", f"{period_elastic:.4f} s")

tab1, tab2, tab3, tab4 = st.tabs([
    "System & Model", "Natural Frequencies", "Mode Shapes", "Time Response"
])

with tab1:
    st.subheader("Physical model")
    st.write(
        "The car and trailer are represented by two translating masses. "
        "The flexible hitch is represented by a massless linear spring. "
        "There is no spring connection to the ground, so the complete assembly "
        "can translate as a rigid body."
    )
    fig, ax = plt.subplots(figsize=(10, 2.7))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")
    # Road
    ax.plot([0.5, 9.5], [0.55, 0.55], linewidth=2)
    for xx in np.arange(0.6, 9.5, 0.35):
        ax.plot([xx, xx + 0.18], [0.42, 0.55], linewidth=0.6)
    # Car and trailer blocks
    ax.add_patch(plt.Rectangle((1.1, 0.85), 2.6, 1.0, fill=False, linewidth=2))
    ax.add_patch(plt.Rectangle((6.3, 0.85), 1.8, 1.0, fill=False, linewidth=2))
    ax.text(2.4, 1.35, f"CAR\nM = {M:g} kg", ha="center", va="center", fontsize=11)
    ax.text(7.2, 1.35, f"TRAILER\nm = {m:g} kg", ha="center", va="center", fontsize=10)
    # Spring zig-zag between bodies
    sx = np.linspace(3.7, 6.3, 13)
    sy = np.array([1.35 + (0.22 if i % 2 else -0.22) for i in range(len(sx))])
    sy[0] = 1.35; sy[-1] = 1.35
    ax.plot(sx, sy, linewidth=1.8)
    ax.text(5.0, 1.8, f"k = {k_kn:g} kN/m", ha="center", fontsize=10)
    ax.text(2.4, 2.25, "x1(t) →", ha="center", fontsize=10)
    ax.text(7.2, 2.25, "x2(t) →", ha="center", fontsize=10)
    ax.set_title("Idealised free-free two-DOF car–trailer model", fontsize=12)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.subheader("Equations of motion")
    st.latex(r"M\ddot{x}_1+k(x_1-x_2)=0")
    st.latex(r"m\ddot{x}_2+k(x_2-x_1)=0")
    st.latex(r"[M]\{\ddot{x}\}+[K]\{x\}=\{0\}")
    st.write("Mass matrix [M] (kg)")
    st.dataframe(Mmat, hide_index=True, use_container_width=True)
    st.write("Stiffness matrix [K] (N/m)")
    st.dataframe(Kmat, hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Characteristic equation")
    st.latex(r"\det([K]-\omega^2[M])=0")
    st.latex(
        r"Mm\omega^4-k(M+m)\omega^2=0"
    )
    st.latex(
        rf"\omega_1=0,\qquad "
        rf"\omega_2=\sqrt{{\frac{{k(M+m)}}{{Mm}}}}"
        rf"= {omega_elastic:.5f}\;\mathrm{{rad/s}}"
    )
    st.latex(
        rf"f_2=\frac{{\omega_2}}{{2\pi}}={freq_elastic:.5f}\;\mathrm{{Hz}}"
    )
    st.latex(
        rf"\mu=\frac{{Mm}}{{M+m}}={mu:.3f}\;\mathrm{{kg}},"
        rf"\qquad \omega_2=\sqrt{{\frac{{k}}{{\mu}}}}"
    )
    st.info(
        "The zero-frequency root is the rigid-body translation mode. "
        "It occurs because the system is not connected to the ground. "
        "The elastic mode is the only non-zero natural frequency."
    )
    st.subheader("Calculated results")
    result_table = {
        "Mode": ["1 - Rigid-body", "2 - Elastic"],
        "Angular frequency (rad/s)": [0.0, omega_elastic],
        "Frequency (Hz)": [0.0, freq_elastic],
        "Period (s)": ["Infinite / undefined", period_elastic],
    }
    st.dataframe(result_table, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Mode-shape vectors")
    st.write("Unnormalised mode shapes (columns correspond to Mode 1 and Mode 2):")
    st.dataframe(
        {"Coordinate": ["Car displacement, x1", "Trailer displacement, x2"],
         "Mode 1": modes[:, 0], "Mode 2": modes[:, 1]},
        hide_index=True, use_container_width=True
    )
    st.write("Mass-normalised mode shapes (units: kg^(-1/2)):")
    st.dataframe(
        {"Coordinate": ["Car", "Trailer"],
         "Mode 1": mass_norm_modes[:, 0],
         "Mode 2": mass_norm_modes[:, 1]},
        hide_index=True, use_container_width=True
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    labels = ["Car", "Trailer"]
    for idx, ax in enumerate(axes):
        vals = modes[:, idx]
        ax.axhline(0, linewidth=0.8)
        ax.bar(labels, vals)
        ax.set_ylabel("Relative modal amplitude")
        ax.set_title("Mode 1: rigid-body" if idx == 0 else "Mode 2: elastic")
        ax.grid(axis="y", alpha=0.25)
        for j, value in enumerate(vals):
            ax.text(j, value + (0.06 if value >= 0 else -0.12),
                    f"{value:.2f}", ha="center", va="center")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("**Physical interpretation**")
    st.write("- Mode 1: car and trailer move together with equal displacement; the hitch does not deform.")
    st.write("- Mode 2: car and trailer move in opposite directions. The displacement ratio is x2/x1 = -M/m.")

    cross = modes[:, 0].T @ Mmat @ modes[:, 1]
    st.metric("Mass-orthogonality check: phi1ᵀ M phi2", f"{cross:.3e}")

with tab4:
    st.subheader("Free-vibration time response")
    st.write(
        "The response is calculated from the undamped equations of motion using "
        "the selected initial displacements and velocities."
    )
    x0 = np.array([x10_mm, x20_mm], dtype=float) / 1000.0
    v0 = np.array([v10_mms, v20_mms], dtype=float) / 1000.0
    y0 = np.concatenate([x0, v0])

    def state_equations(t, y):
        x = y[:2]
        v = y[2:]
        a = np.linalg.solve(Mmat, -Kmat @ x)
        return np.concatenate([v, a])

    t_eval = np.linspace(0.0, duration, 700)
    sol = solve_ivp(state_equations, (0.0, duration), y0,
                    t_eval=t_eval, rtol=1e-8, atol=1e-10)
    x1_mm = sol.y[0] * 1000.0
    x2_mm = sol.y[1] * 1000.0

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sol.t, x1_mm, label="Car x1(t)")
    ax.plot(sol.t, x2_mm, label="Trailer x2(t)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Displacement (mm)")
    ax.set_title("Displacement response versus time")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("### Animated car–trailer motion")
    st.write(
        "Press **Play** below the diagram to watch the car and trailer move continuously. "
        "The spring changes length as the relative displacement changes. Use **Pause** "
        "to stop the animation, or the timeline to inspect any instant."
    )

    # Plotly frames animate the body positions and the connecting spring in the browser.
    # A display scale is used only to make small physical displacements visible.
    display_scale = 0.055  # drawing units per millimetre
    base_car_x = 0.6
    base_trailer_x = 5.2
    car_width, trailer_width, body_height = 2.0, 1.55, 0.78
    road_y = 0.0
    y_center = road_y + body_height / 2

    # Keep the visual geometry from overlapping for large user-entered initial conditions.
    max_abs_mm = max(float(np.max(np.abs(x1_mm))), float(np.max(np.abs(x2_mm))), 1.0)
    display_scale = min(display_scale, 1.8 / max_abs_mm)

    frames = []
    frame_indices = np.linspace(0, len(sol.t) - 1, 100, dtype=int)
    frame_indices = np.unique(frame_indices)

    for frame_no, idx in enumerate(frame_indices):
        car_disp_mm = x1_mm[idx]
        trailer_disp_mm = x2_mm[idx]
        car_x = base_car_x + display_scale * car_disp_mm
        trailer_x = base_trailer_x + display_scale * trailer_disp_mm

        spring_start = car_x + car_width
        spring_end = trailer_x
        spring_x = np.linspace(spring_start, spring_end, 17)
        spring_y = np.array([
            y_center + (0.16 if j % 2 else -0.16)
            for j in range(len(spring_x))
        ])
        spring_y[0] = y_center
        spring_y[-1] = y_center

        # Shapes: road, car body, trailer body, wheels, and connecting spring.
        shapes = [
            dict(type="line", x0=-0.4, y0=road_y-0.12, x1=9.2, y1=road_y-0.12,
                 line=dict(width=3)),
            dict(type="rect", x0=car_x, y0=road_y+0.12,
                 x1=car_x+car_width, y1=road_y+0.12+body_height,
                 line=dict(width=3), fillcolor="rgba(80,140,220,0.16)"),
            dict(type="rect", x0=trailer_x, y0=road_y+0.12,
                 x1=trailer_x+trailer_width, y1=road_y+0.12+body_height,
                 line=dict(width=3), fillcolor="rgba(230,160,60,0.16)"),
        ]
        for wx in [car_x+0.42, car_x+1.58]:
            shapes.append(dict(type="circle", x0=wx-0.15, y0=road_y-0.03,
                               x1=wx+0.15, y1=road_y+0.27,
                               line=dict(width=2), fillcolor="white"))
        for wx in [trailer_x+0.32, trailer_x+1.22]:
            shapes.append(dict(type="circle", x0=wx-0.13, y0=road_y-0.02,
                               x1=wx+0.13, y1=road_y+0.24,
                               line=dict(width=2), fillcolor="white"))

        frames.append(go.Frame(
            name=str(frame_no),
            data=[
                go.Scatter(x=spring_x, y=spring_y, mode="lines",
                           line=dict(width=4), name="Hitch spring"),
                go.Scatter(x=[car_x+car_width/2], y=[road_y+0.12+body_height/2],
                           mode="text", text=[f"CAR<br>M = {M:g} kg"],
                           textfont=dict(size=13), name="Car label"),
                go.Scatter(x=[trailer_x+trailer_width/2],
                           y=[road_y+0.12+body_height/2],
                           mode="text", text=[f"TRAILER<br>m = {m:g} kg"],
                           textfont=dict(size=12), name="Trailer label"),
            ],
            layout=go.Layout(
                shapes=shapes,
                annotations=[
                    dict(x=car_x+car_width/2, y=1.45, text=f"x1 = {car_disp_mm:.2f} mm",
                         showarrow=False),
                    dict(x=trailer_x+trailer_width/2, y=1.72,
                         text=f"x2 = {trailer_disp_mm:.2f} mm", showarrow=False),
                    dict(x=(spring_start+spring_end)/2, y=1.12,
                         text=f"k = {k_kn:g} kN/m", showarrow=False),
                    dict(x=4.4, y=2.15, text=f"Time = {sol.t[idx]:.2f} s",
                         showarrow=False, font=dict(size=14)),
                ]
            )
        ))

    # Initial frame geometry.
    initial_idx = frame_indices[0]
    initial_car_x = base_car_x + display_scale * x1_mm[initial_idx]
    initial_trailer_x = base_trailer_x + display_scale * x2_mm[initial_idx]
    initial_sx = np.linspace(initial_car_x+car_width, initial_trailer_x, 17)
    initial_sy = np.array([
        y_center + (0.16 if j % 2 else -0.16) for j in range(len(initial_sx))
    ])
    initial_sy[0] = y_center
    initial_sy[-1] = y_center
    initial_shapes = [
        dict(type="line", x0=-0.4, y0=road_y-0.12, x1=9.2, y1=road_y-0.12,
             line=dict(width=3)),
        dict(type="rect", x0=initial_car_x, y0=road_y+0.12,
             x1=initial_car_x+car_width, y1=road_y+0.12+body_height,
             line=dict(width=3), fillcolor="rgba(80,140,220,0.16)"),
        dict(type="rect", x0=initial_trailer_x, y0=road_y+0.12,
             x1=initial_trailer_x+trailer_width, y1=road_y+0.12+body_height,
             line=dict(width=3), fillcolor="rgba(230,160,60,0.16)"),
    ]
    for wx in [initial_car_x+0.42, initial_car_x+1.58]:
        initial_shapes.append(dict(type="circle", x0=wx-0.15, y0=road_y-0.03,
                                   x1=wx+0.15, y1=road_y+0.27,
                                   line=dict(width=2), fillcolor="white"))
    for wx in [initial_trailer_x+0.32, initial_trailer_x+1.22]:
        initial_shapes.append(dict(type="circle", x0=wx-0.13, y0=road_y-0.02,
                                   x1=wx+0.13, y1=road_y+0.24,
                                   line=dict(width=2), fillcolor="white"))

    animation_fig = go.Figure(
        data=[
            go.Scatter(x=initial_sx, y=initial_sy, mode="lines",
                       line=dict(width=4), name="Hitch spring"),
            go.Scatter(x=[initial_car_x+car_width/2],
                       y=[road_y+0.12+body_height/2], mode="text",
                       text=[f"CAR<br>M = {M:g} kg"], textfont=dict(size=13),
                       name="Car label"),
            go.Scatter(x=[initial_trailer_x+trailer_width/2],
                       y=[road_y+0.12+body_height/2], mode="text",
                       text=[f"TRAILER<br>m = {m:g} kg"], textfont=dict(size=12),
                       name="Trailer label"),
        ],
        frames=frames
    )
    animation_fig.update_layout(
        height=390,
        title="Live free-vibration animation — press Play",
        xaxis=dict(range=[-0.5, 9.4], visible=False, fixedrange=True),
        yaxis=dict(range=[-0.35, 2.55], visible=False, fixedrange=True),
        shapes=initial_shapes,
        annotations=[
            dict(x=initial_car_x+car_width/2, y=1.45,
                 text=f"x1 = {x1_mm[initial_idx]:.2f} mm", showarrow=False),
            dict(x=initial_trailer_x+trailer_width/2, y=1.72,
                 text=f"x2 = {x2_mm[initial_idx]:.2f} mm", showarrow=False),
            dict(x=4.4, y=2.15, text=f"Time = {sol.t[initial_idx]:.2f} s",
                 showarrow=False, font=dict(size=14)),
        ],
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.08, y=-0.16,
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, {"frame": {"duration": 40, "redraw": True},
                                  "fromcurrent": True,
                                  "transition": {"duration": 0}}]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}]),
            ]
        )],
        sliders=[dict(
            x=0.28, y=-0.16, len=0.68,
            currentvalue=dict(prefix="Frame: "),
            steps=[
                dict(method="animate", args=[[str(i)],
                     {"mode": "immediate", "frame": {"duration": 0, "redraw": True},
                      "transition": {"duration": 0}}],
                     label=f"{sol.t[idx]:.2f}")
                for i, idx in enumerate(frame_indices)
            ]
        )],
        margin=dict(l=20, r=20, t=65, b=90),
    )
    st.plotly_chart(animation_fig, use_container_width=True)

    st.caption(
        "The animation uses a display scale so the motion is visible; "
        "the displacement values and time-response graph remain in physical units."
    )

st.divider()
st.caption(
    "ME4131 - Mechanical Vibration | Group 1 (Resonance Duo). "
    "Model assumptions: rigid masses, linear massless spring, no damping, "
    "no external force, and horizontal translation only."
)
