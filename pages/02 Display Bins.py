import streamlit as st
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
from math import radians, sin, cos, sqrt, atan2

# ✅ Check if user session is valid
if "predicted_class" not in st.session_state or "uid" not in st.session_state:
    st.error("Missing user session or classification. Please classify waste first.")
    st.stop()

predicted_class1 = st.session_state["predicted_class"]
user_uid = st.session_state["uid"]

st.title("Nearby Bins - Waste Type Match")
st.info(f"Predicted Waste Class: **{predicted_class1}**")

# ✅ Initialize Firebase DB reference
db_ref = db.reference("/bins")

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# Step 1: Select current location
st.subheader("Select Your Current Location")
map_input = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
map_input.add_child(folium.LatLngPopup())
map_result = st_folium(map_input, height=350, width=700)

if map_result and map_result.get("last_clicked"):
    current_latlon = map_result["last_clicked"]
    user_lat, user_lon = current_latlon["lat"], current_latlon["lng"]
    st.success(f"Selected Location: ({user_lat:.4f}, {user_lon:.4f})")

    # Step 2: Fetch and filter matching bins
    st.subheader("Matching Bins Nearby (within 10 km)")
    all_bins = db_ref.get()
    matching_bins = []

    for bin_id, bin_data in all_bins.items():
        if bin_data.get("type", "").lower() == predicted_class1.lower():
            loc = bin_data.get("location", {})
            lat = loc.get("lat")
            lon = loc.get("lon")
            if lat is not None and lon is not None:
                distance = haversine_distance(user_lat, user_lon, lat, lon)
                if distance <= 10:
                    matching_bins.append((distance, bin_id, bin_data))

    if not matching_bins:
        st.warning("No matching bins found within 10 km.")
    else:
        # Show map with bins
        m = folium.Map(location=[user_lat, user_lon], zoom_start=13)

        # Mark user location
        folium.Marker(
            location=[user_lat, user_lon],
            popup="You",
            icon=folium.Icon(color="blue")
        ).add_to(m)

        for _, bin_id, bin_data in matching_bins:
            lat = bin_data["location"]["lat"]
            lon = bin_data["location"]["lon"]
            fill = bin_data.get("fill_percentage", "N/A")
            bin_type = bin_data.get("type", "Unknown")

            popup_html = f"""
                <b>Type:</b> {bin_type}<br>
                <b>Lat:</b> {lat}<br>
                <b>Lon:</b> {lon}<br>
                <b>Fill %:</b> {fill}%
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color="green")
            ).add_to(m)

        st_folium(m, height=1000, width=1800)

        # ✅ Add button to move to deposit page
        if st.button("Proceed to Deposit Waste"):
            # (Optional) Could store location or bin info too
            st.switch_page("pages/03 Depost Waste.py")
