#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Author: Sneh Kr
Github: https://github.com/snehkr/GrabFreeProxy
Copyright (c) 2025 snehkr
This script fetches proxies from multiple sources, checks their availability by attempting to access common websites,
"""

from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from operator import itemgetter
from datetime import datetime, timezone
import json, requests, aiohttp, re, asyncio, time, ipaddress, os
from bs4 import BeautifulSoup

# Configuration
TIMEOUT = 10  # seconds
CHECK_URLS = [
    (
        "google",
        "http://www.google.com/",
    ),
    (
        "facebook",
        "http://www.facebook.com/",
    ),
]


def verify_ip_port(ip: str, port: str) -> bool:
    """Validate IP address and port."""
    try:
        ipaddress.ip_address(ip)
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, ipaddress.AddressValueError):
        return False


class Source:
    url = ""
    ip_pat = re.compile(r"\s?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*")

    def read_url(self):
        data = None
        if self.url:
            try:
                with urlopen(self.url) as handler:
                    data = handler.read().decode("utf-8")
            except (HTTPError, URLError):
                pass
        return data

    def read_mech_url(self, extra_headers=None):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) "
                "Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1"
            )
        }

        if extra_headers:
            headers.update(dict(extra_headers))

        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching {self.url}: {e}")
            return None

    def get_data(self):
        raise NotImplementedError


class SpyList(Source):
    """Get proxies from spys.me"""

    url = "https://spys.me/proxy.txt"

    def get_data(self):
        data = self.read_url()
        result = list()
        if data:
            for line in data.split("\n"):
                if self.ip_pat.match(line):
                    try:
                        ip, port = line.split()[0].split(":")
                        result.append((ip, port))
                    except ValueError:
                        pass
        return result if result else []


class FreeProxyList(Source):
    """Get proxies from free-proxy-list.net"""

    url = "https://free-proxy-list.net"

    def read_url(self):
        return self.read_mech_url()

    def get_data(self):
        data = self.read_url()
        soup = BeautifulSoup(data, "lxml")

        table = soup.find("table", class_="table table-striped table-bordered")
        if not table:
            print("❌ Table not found.")
            return []

        result = []
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 2:
                td_ip = tds[0].text.strip()
                td_port = tds[1].text.strip()
                if self.ip_pat.match(td_ip):
                    result.append((td_ip, td_port))
        return result if result else []


class ProxyDailyList(Source):
    """Get proxies from proxy-daily.com"""

    def get_data(self):

        headers = {
            "accept": "application/json",
            "referer": "https://proxy-daily.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        params = (
            ("draw", "0"),
            ("columns[0][data]", "ip"),
            ("columns[0][name]", "ip"),
            ("columns[0][searchable]", "true"),
            ("columns[0][orderable]", "false"),
            ("columns[0][search][value]", ""),
            ("columns[0][search][regex]", "false"),
            ("columns[1][data]", "port"),
            ("columns[1][name]", "port"),
            ("columns[1][searchable]", "true"),
            ("columns[1][orderable]", "false"),
            ("columns[1][search][value]", ""),
            ("columns[1][search][regex]", "false"),
            ("columns[2][data]", "protocol"),
            ("columns[2][name]", "protocol"),
            ("columns[2][searchable]", "true"),
            ("columns[2][orderable]", "false"),
            ("columns[2][search][value]", ""),
            ("columns[2][search][regex]", "false"),
            ("columns[3][data]", "speed"),
            ("columns[3][name]", "speed"),
            ("columns[3][searchable]", "true"),
            ("columns[3][orderable]", "false"),
            ("columns[3][search][value]", ""),
            ("columns[3][search][regex]", "false"),
            ("columns[4][data]", "anonymity"),
            ("columns[4][name]", "anonymity"),
            ("columns[4][searchable]", "true"),
            ("columns[4][orderable]", "false"),
            ("columns[4][search][value]", ""),
            ("columns[4][search][regex]", "false"),
            ("columns[5][data]", "country"),
            ("columns[5][name]", "country"),
            ("columns[5][searchable]", "true"),
            ("columns[5][orderable]", "false"),
            ("columns[5][search][value]", ""),
            ("columns[5][search][regex]", "false"),
            ("start", "0"),
            ("length", "50"),
            ("search[value]", ""),
            ("search[regex]", "false"),
            ("_", int(time.time() * 1000)),
        )

        response = requests.get(
            "https://proxy-daily.com/api/serverside/proxies",
            headers=headers,
            params=params,
        ).json()

        result = []

        for item in response["data"]:
            ip = item["ip"]
            port = item["port"]
            if self.ip_pat.match(ip):
                result.append((ip, port))

        return result if result else []


async def check_proxy(proxy):
    """Try to load content of several commonly known websites through proxy"""

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    result = dict()
    ip, port = proxy
    result["ip"] = ip
    result["port"] = port
    result["last_checked"] = datetime.now(timezone.utc).isoformat()

    for website_name, url in CHECK_URLS:
        try:
            async with aiohttp.ClientSession(
                timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                start = time.time()
                status_code = 404
                total_time = None
                error_msg = "no"
                async with session.get(
                    url, proxy="http://{}:{}".format(ip, port)
                ) as resp:
                    status_code = resp.status
                    await resp.text()
                    end = time.time()
                    total_time = int(round(end - start, 2) * 1000)
        except asyncio.TimeoutError:
            status_code = 408
            error_msg = "timeout error"
        except aiohttp.client_exceptions.ClientProxyConnectionError:
            error_msg = "connection error"
            status_code = 503
        except Exception as e:
            status_code = 503
            error_msg = "unknown error: {}.".format(e)
        finally:
            result[website_name + "_status"] = status_code
            result[website_name + "_error"] = error_msg
            result[website_name + "_total_time"] = total_time
    return result


async def runner(complete_list):
    tasks = [check_proxy(item) for item in complete_list]
    return await asyncio.gather(*tasks)


def main():
    result = []

    sources = [
        FreeProxyList().get_data,
        SpyList().get_data,
        ProxyDailyList().get_data,
    ]

    for job in sources:
        result += job()

    complete_list = list(set(tuple(result)))
    filtered_list = filter(lambda x: verify_ip_port(*x), complete_list)

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(runner(filtered_list))
    finally:
        loop.close()
    return result


if __name__ == "__main__":
    data = main()

    try:
        errorless_measures = [
            sum(
                item[resource + "_error"] == "no"
                for resource in map(itemgetter(0), CHECK_URLS)
            )
            for item in data
        ]
        arg_sorted = sorted(
            range(len(errorless_measures)),
            key=errorless_measures.__getitem__,
            reverse=True,
        )
        sorted_data = [data[ind] for ind in arg_sorted]
    except KeyError:
        pass

    to_json = {
        "status": "success",
        "version": "1.0.0",
        "description": "List of free proxies with status information",
        "author": "snehkr",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "proxies": sorted_data,
    }

    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "gfp_proxy.json"), "w") as f:
        f.write(json.dumps(to_json, sort_keys=True, indent=4))
