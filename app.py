import streamlit as st
import requests

st.title("Proxy Checker")

# Input field for proxy address
proxy_input = st.text_input("Enter proxy (ip:port):", "")

# Button to trigger the check
if st.button("Check Proxy"):
    # Basic validation of input
    if ':' not in proxy_input:
        st.error("Please enter the proxy in the correct format: ip:port")
    else:
        ip, port = proxy_input.split(':', 1)
        proxies = {
            "http": f"http://{ip}:{port}",
            "https": f"http://{ip}:{port}"
        }
        test_url = "http://httpbin.org/ip"

        with st.spinner("Checking proxy..."):
            try:
                response = requests.get(test_url, proxies=proxies, timeout=5)
                if response.status_code == 200:
                    origin_ip = response.json().get('origin', 'Unknown')
                    st.success(f"✅ Proxy {proxy_input} is working!\nYour IP as seen by the test server: {origin_ip}")
                else:
                    st.error(f"❌ Proxy {proxy_input} returned status code {response.status_code}. Might not be working.")
            except requests.RequestException as e:
                st.error(f"❌ Proxy {proxy_input} is not working. Error: {e}")
