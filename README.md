## 🌟 GrabFreeProxy : Hourly Updated Free Proxy Server List

![GitHub last commit](https://img.shields.io/github/last-commit/snehkr/GrabFreeProxy?color=green)
![JSON Format](https://img.shields.io/badge/Format-JSON-blue)
![Proxy Count](https://img.shields.io/badge/Proxies-100%2B-brightgreen)

A lightning-fast tool that collects, verifies, and delivers fresh proxy servers daily. Perfect for web scraping, automation, and privacy protection.

## 📌 Features

- ✅ `Hourly Updated` – Fresh proxy list updated every day
- ✅ `Fully Tested` – Each proxy is checked against multiple websites
- ✅ `Performance Metrics` – Includes response time, status codes, and errors
- ✅ `Easy Integration` – Simple JSON format for seamless use in your projects

## 📂 File Structure `(gfp_proxy.json)`

```json
{
  "status": "success",
  "version": "1.0.0",
  "author": "snehkr",
  "description": "List of free proxies with status information",
  "proxies": [
    {
      "ip": "xxx.xxx.xxx.xxx",
      "port": "xxxx",
      "example_error": "no",
      "example_status": 403,
      "example_total_time": 10130,
      "google_error": "no",
      "google_status": 200,
      "google_total_time": 2760,
      "last_checked": "2025-06-06T13:34:54.541506+00:00"
    }
  ],
  "generated_at": "2025-06-06T13:34:54.541506+00:00"
}
```

- `*_total_time` Response time in milliseconds
- `*_error` Error message if connection failed
- `*_status` HTTP status code (200, 407, etc.)
- `last_checked	` UTC timestamp of last verification

## 🚀 How to Use

1.  Direct JSON Access

    - You can fetch the latest proxy list directly via:

      ```md
      https://minify.snehkr.in/gfp_proxy.json
      ```

2.  Python Example (Using requests)

    ```py
    import requests

    url = "https://minify.snehkr.in/gfp_proxy.json"
    response = requests.get(url)
    proxy_data = response.json()

    for proxy in proxy_data["proxies"]:
    print(f"IP: {proxy['ip']}:{proxy['port']} | Google Status: {proxy['google_status']} | Response Time: {proxy['google_total_time']}ms")
    ```

## 🔍 Why Use This?

- ✔ `Reliable` – Proxies are tested against google.com, jiotv.com, and tataplay.com
- ✔ `Fast` – Asynchronous checks ensure quick validation
- ✔ `Transparent` – Clear error reporting and performance metrics

## ⭐ Star this repo if you find it useful!

- GitHub : [snehkr/GrabFreeProxy](https://github.com/snehkr/GrabFreeProxy)

## 🤝 Contributing

- Found a bug? Want to improve the project?
- 👉 [Open an Issue](https://github.com/snehkr/GrabFreeProxy/issues) or Submit a PR!

## 📜 License

- This project is open-source and free to use. Contributions are welcome!

</br>

<h4 align="center">
  © GrabFreeProxy - 2025 </br>
</h4>

<p align="center">
  🌟 Happy Proxy Surfing! 🌟</br>
  CODED WITH ❤️ BY SNEH KR 
</p>
