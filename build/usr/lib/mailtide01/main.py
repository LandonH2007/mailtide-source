# mailtide/main.py

VERSION = "v1.0.0"

# Imports
import imaplib
import email
from email.header import decode_header
from email.message import EmailMessage
import re
import sys
import curses
import time
import html2text
import os
import smtplib
import mimetypes

# Add vendor to path
sys.path.insert(0, "/usr/bin/lib/mailtide01/vendor")

# Services

services = {
	"@yahoo.com": "imap.mail.yahoo.com",
	"@gmail.com": "imap.gmail.com",
	"@outlook.com": "imap-mail.outlook.com",
	"@hotmail.com": "imap-mail.outlook.com",
	"@live.com": "imap-mail.outlook.com",
	"@icloud.com": "imap.mail.me.com",
	"@me.com": "imap.mail.me.com",
	"@aol.com": "imap.aol.com",
	"@zoho.com": "imap.zoho.com",
	"@protonmail.com": "imap.protonmail.com",
	"@gmx.com": "imap.gmx.com",
	"@gmx.net": "imap.gmx.com",
	"@mail.com": "imap.mail.com",
	"@yandex.com": "imap.yandex.com",
	"@yandex.ru": "imap.yandex.com",
	"@fastmail.com": "imap.fastmail.com",
}

# CREDENTIALS
EMAIL_USER = "NONE"
EMAIL_PASS = "yoou mlnn ogjr udzu"
CURRENT_FOLDER = "NONE"


COMPOSING = False
subject = ""
recipients = []
screen_objs = []

attachments = []

def main():
	global CURRENT_FOLDER, EMAIL_USER, EMAIL_PASS
	print("Starting Mailtide...")
	curses.wrapper(ui)

def ui(stdscr):
	global CURRENT_FOLDER, EMAIL_USER, EMAIL_PASS, screen_objs, COMPOSING, subject, recipients, attachments
	snr = None
	page = 0
	max_pages = 0
	curses.curs_set(0)
	stdscr.nodelay(True)
	curses.start_color()

	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
	curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
	
	stdscr.clear()
	stdscr.refresh()

	input_mode = False
	user_input = ""

	text = f"Mailtide {VERSION}										"
	stdscr.addstr(0, 0, text, curses.color_pair(1))

	start = time.time()

	prev_max_y, prev_max_x = stdscr.getmaxyx()

	# Main loop
	while True:
		max_y, max_x = stdscr.getmaxyx()

		# If screen size changed, clear and redraw
		if (max_y, max_x) != (prev_max_y, prev_max_x):
			stdscr.clear()
			prev_max_y, prev_max_x = max_y, max_x

		stdscr.addstr(0, 0, text.ljust(max_x), curses.color_pair(1))
		stdscr.addstr(1, 0, f"Logged in as {EMAIL_USER}".ljust(max_x), curses.color_pair(1))
		stdscr.addstr(2, 0, f"Seeing folder {CURRENT_FOLDER}".ljust(max_x), curses.color_pair(1))
		if snr is not None:
			if isinstance(snr, tuple):
				mail = snr[0]
				screen_objs = [snr[1]]
				snr = None
			elif isinstance(snr, str):
				screen_objs = [snr]
				snr = None
		else:
			stdscr.addstr(max_y - 4, 0, " ".ljust(max_x), curses.color_pair(1))

		if not COMPOSING:
			stdscr.addstr(max_y - 3, 0, "S: Sign In 	O: Sign Out 	L: List Folders 	F: Enter Folder		V: Page Down 	T: Page Up    R: Read    M: Move".ljust(max_x), curses.color_pair(1))
			stdscr.addstr(max_y - 2, 0, "E: Load and list    Q: Quit    r: Refresh     C: Compose     D: Download Attachment".ljust(max_x), curses.color_pair(1))
			if input_mode == "S":
				stdscr.addstr(max_y - 1, 0, ("Enter Address: " + user_input + "_"))
			elif input_mode == "S2":
				stdscr.addstr(max_y - 1, 0, ("Enter Password: " + user_input + "_"))
			elif input_mode == "F":
				stdscr.addstr(max_y - 1, 0, ("Enter Folder: " + user_input + "_"))
			elif input_mode == "R":
				stdscr.addstr(max_y - 1, 0, ("Enter Email Id: " + user_input + "_"))
			elif input_mode == "M":
				stdscr.addstr(max_y - 1, 0, ("Enter Email Id: " + user_input + "_"))
			elif input_mode == "M2":
				stdscr.addstr(max_y - 1, 0, ("Enter Folder: " + user_input + "_"))
			elif input_mode == "D":
				stdscr.addstr(max_y - 1, 0, ("Enter Email Id: " + user_input + "_"))
			elif input_mode == "C":
				stdscr.addstr(max_y - 1, 0, ("Enter Subject: " + user_input + "_"))
			elif input_mode == "C2":
				stdscr.addstr(max_y - 1, 0, ("Recipients (separated by spaces): " + user_input + "_"))

		else: 
			stdscr.addstr(max_y - 3, 0, f"Writing Message. Subject: {subject}".ljust(max_x), curses.color_pair(1))
			stdscr.addstr(max_y - 2, 0, "^s: Save as Draft 	^l: Load Draft 	^g: Send    ^a: Attach    ^x: Exit".ljust(max_x), curses.color_pair(1))
			if input_mode == "CTRL_A":
				stdscr.addstr(max_y - 1, 0, ("Enter Attachment Path: " + user_input + "_"))
		# Render Objects
		# Clear main area before rendering screen objects
		for i in range(4, max_y - 5):
			stdscr.move(i, 0)
			stdscr.clrtoeol()

		max_pages = 0
		display_lines = []
		for obj in screen_objs[page:]:
			
			if isinstance(obj, str):
				if "\n" in obj:
					obj = re.sub(r'[^\S ]+$', '', obj)
				# Split long lines to fit the screen width
				while len(obj) > max_x:
					display_lines.append(obj[:max_x])
					obj = obj[max_x:]
				display_lines.append(obj)
			else:
				display_lines.append(str(obj))

		for i, val in enumerate(display_lines):
			line = 4 + (i - page)
			if 0 <= line < max_y - 5:
				if val == "!":
					stdscr.addstr(line, 0, f"{' ' * max_x}", curses.color_pair(2))
				else:
					stdscr.addstr(line, 0, f"{val}".ljust(max_x))
			else:
				max_pages += 1
		stdscr.addstr(max_y - 4, 0, f"{page}/{max_pages}".ljust(max_x), curses.color_pair(1))
		if page > max_pages:
			page = max_pages

		stdscr.refresh()

		key = stdscr.getch()

		if not COMPOSING:
			if input_mode:
				if key in (10, 13):  # Enter key
					stdscr.addstr(max_y - 1, 0, (f"{" "*(max_x-1)}"))
					if input_mode == "S":
						username = user_input
						user_input = ""
						input_mode = "S2"
					elif input_mode == "D":
						screen_objs = download_attachments(mail=mail, eid=user_input)
						input_mode = None
						user_input = ""
					elif input_mode == "S2":
						snr = signin(username=username, password=user_input)
						user_input = ""
						input_mode = None
					elif input_mode == "F":
						CURRENT_FOLDER = user_input
						user_input = ""
						input_mode = None
					elif input_mode == "R":
						if user_input in eids:
							screen_objs = get_email_body(all_msg[eids.index(user_input)])
						else:
							screen_objs = ["EMail not found."]
						user_input = ""
						input_mode = None
					elif input_mode == "M":
						email_id = user_input
						user_input = ""
						input_mode = "M2"
					elif input_mode == "M2":
						tag = user_input
						user_input = ""
						screen_objs = move_email(mail, all_msg[eids.index(email_id)], email_id, tag)
						input_mode = None
					elif input_mode == "C":
						subject = user_input
						user_input = ""
						input_mode = "C2"
					elif input_mode == "C2":
						recipients = user_input.split()
						COMPOSING = True
						user_input = ""
						input_mode = None
					else:
						user_input = ""
						input_mode = None
				elif 32 <= key <= 126:
					user_input += chr(key)
				elif key in (curses.KEY_BACKSPACE, 127, 8):
					user_input = user_input[:-1]
			else:
				if key == ord('S'):
					input_mode = "S"
					user_input = ""
				elif key == ord("F"):
					if not EMAIL_USER == "NONE":
						input_mode = "F"
						user_input = ""
					else:
						screen_objs = ["Please sign in to view EMails"]
				elif key == ord("D"):
					if not EMAIL_USER == "NONE":
						input_mode = "D"
						user_input = ""
					else:
						screen_objs = ["Please sign in to view EMails"]
				elif key == ord("R"):
					if not EMAIL_USER == "NONE":
						input_mode = "R"
						user_input = ""
					else:
						screen_objs = ["Please sign in to view EMails"]
				elif key == ord("M"):
					if not EMAIL_USER == "NONE":
						input_mode = "M"
						user_input = ""
					else:
						screen_objs = ["Please sign in to view EMails"]
				elif key == ord("L"):
					if not EMAIL_USER == "NONE" and 'mail' in locals() and mail is not None:
						try:
							screen_objs = list_folders(mail=mail)
						except Exception as e:
							screen_objs = [f"Error listing folders: {e}"]
					else:
						screen_objs = ["Please sign in to view EMails"]
				elif key == ord("C"):
					if not EMAIL_USER == "NONE" and 'mail' in locals() and mail is not None:
						input_mode = "C"
						user_input = ""
						attachments = []
						recipients = []
						screen_objs = [""]
						pos = 0
					else:
						screen_objs = ["Please sign in to write EMails"]

				elif key == ord("E"):
					if not EMAIL_USER == "NONE" and 'mail' in locals() and mail is not None:
						try:
							screen_objs, all_msg, eids = get_folder_cont(mail, folder=CURRENT_FOLDER)
						except Exception as e:
							screen_objs = [f"Error loading folder: {e}"]
							all_msg, eids = [], []
					else:
						screen_objs = ["Please sign in to view EMails"]
				elif key == ord("Q"):
					exit()
				elif key == ord("O"):
					EMAIL_USER = "NONE"
					CURRENT_FOLDER = "NONE"
					if 'mail' in locals() and mail is not None:
						try:
							mail.logout()
						except Exception:
							pass
				elif key == ord("r"):
					screen_objs, all_msg, eids = get_folder_cont(mail, CURRENT_FOLDER)

		
		if key == ord("V") and not (page + 1) > max_pages:
				page += 1
		elif key == ord("T") and not (page - 1) < 0:
				page -= 1
		if COMPOSING:
			if input_mode:
				if 32 <= key <= 126:
					user_input += chr(key)
				elif key in (curses.KEY_BACKSPACE, 127, 8):
					user_input = user_input[:-1]
				if key in (10, 13):
					stdscr.addstr(max_y - 1, 0, (f"{" "*(max_x-1)}"))
					if input_mode == "CTRL_A":
						attachments.append(os.path.expanduser(user_input))
						input_mode = None
			screen_objs[pos] = (user_input + "_")
			if not input_mode:
				if 32 <= key <= 126:
					user_input += chr(key)
				elif key in (curses.KEY_BACKSPACE, 127, 8):
					try:
						user_input = user_input[:-1]
					except IndexError:
						user_input = ""
				elif key == curses.KEY_DOWN and (pos + 1) < len(screen_objs):
					screen_objs[pos] = screen_objs[pos][:-1]
					pos += 1
					user_input = screen_objs[pos]
				elif key == curses.KEY_UP and (pos - 1) >= 0:
					screen_objs[pos] = screen_objs[pos][:-1]
					pos -= 1
					user_input = screen_objs[pos]
				elif key in (10, 13):
					if (pos + 1) >= len(screen_objs):
						screen_objs.append("")
						screen_objs[pos] = screen_objs[pos][:-1] + "\n"
						pos += 1
					if pos < len(screen_objs):
						user_input = screen_objs[pos]
					else:
						user_input = ""

				if key == ord('\t'):
					user_input = user_input + "\t"
				if key == (ord('s') & 0x1f):
					with open(f"{subject}.txt", "w") as file:
						screen_objs.append(recipients)
						file.writelines(screen_objs)
						screen_objs = screen_objs [:-1]
				if key == (ord('l') & 0x1f):
					with open(f"{subject}.txt", "w") as file:
						screen_objs.append(recipients)
						file.writelines(screen_objs)
						screen_objs = screen_objs [:-1]
				if key == (ord('a') & 0x1f):
					user_input = ""
					input_mode = "CTRL_A"
				if key == (ord('g') & 0x1f):
					COMPOSING, screen_objs = send(screen_objs, recipients, subject, attachments)
				if key == (ord('x') & 0x1f):
					COMPOSING = False
					screen_objs = []


		stdscr.clrtoeol()


def get_email_body(msg):

	message = []
	found_plain = False

	if msg.is_multipart():
		for part in msg.walk():
			content_type = part.get_content_type()
			content_disposition = str(part.get("Content-Disposition"))
			if content_type == "text/plain" and "attachment" not in content_disposition:
				try:
					body = part.get_payload(decode=True).decode(errors="replace")
					for line in body.splitlines():
						message.append(line.strip())
					found_plain = True
				except Exception:
					return ["Could not decode plain text"]
		if found_plain:
			return message
		# Try to extract HTML if no plain text found
		for part in msg.walk():
			content_type = part.get_content_type()
			content_disposition = str(part.get("Content-Disposition"))
			if content_type == "text/html" and "attachment" not in content_disposition:
				try:
					html = part.get_payload(decode=True).decode(errors="replace")
					text = html2text.html2text(html)
					return [line.strip() for line in text.splitlines() if line.strip()]
				except Exception:
					return ["Could not decode HTML part"]
		return ["No readable text found"]
	else:
		# Not multipart - try plain, then html
		try:
			return [msg.get_payload(decode=True).decode(errors="replace")]
		except Exception:
			if msg.get_content_type() == "text/html":
				try:
					html = msg.get_payload(decode=True).decode(errors="replace")
					text = html2text.html2text(html)
					return [line.strip() for line in text.splitlines() if line.strip()]
				except Exception:
					return ["Could not decode HTML body"]
			return ["Could not decode message body"]

def get_folder_cont(mail, folder='INBOX'):
	status, data = mail.select(f'"{folder}"')
	if status != "OK":
		return ["Folder does not exist."], None, None
	elif data == [b'0']:
		return ["Folder is empty."], None, None
	status, messages = mail.search(None, "ALL")
	msg_summary = []
	all_msg = []
	eids = []

	email_ids = messages[0].split()
	latest = email_ids
	for eid in reversed(latest):
		eid_str = eid.decode() if isinstance(eid, bytes) else str(eid)
		status, msg_data = mail.fetch(eid, "(RFC822)")
		for response_part in msg_data:
			if isinstance(response_part, tuple):
				msg = email.message_from_bytes(response_part[1])
				all_msg.append(msg)
				subject, encoding = decode_header(msg["Subject"])[0]
				if isinstance(subject, bytes):
					subject = subject.decode(encoding or "utf-8")
				from_ = msg.get("From")
				msg_summary.append(f"[{eid_str}] - From: {from_}")
				msg_summary.append(f"          Subject: {subject}")
				msg_summary.append(f"          Attatchments: {has_attachment(msg=msg)}")
				msg_summary.append("!")
				eids.append(eid_str)
	return msg_summary, all_msg, eids

def signin(username, password):
	global EMAIL_USER, EMAIL_PASS
	if EMAIL_USER == "NONE":
		try:
			service = "@" + username.split("@", 1)[1]
			if service in services:
				
				mail = imaplib.IMAP4_SSL(services[service])
				mail.login(username, password)
				EMAIL_USER = username
				EMAIL_PASS = password
				return mail, f"Logged into {EMAIL_USER} successfully."
			else:
				return "Login failed: Provided EMail is not supported."
		except imaplib.IMAP4.error as e:
			return f"Login failed: {e}. If you have 2-Factor Authentication enabled, try generating and using an App Password instead."
	else:
		return f"Login failed: Already logged into an EMail account. {EMAIL_USER}"

def list_folders(mail):
	all_folders = []
	# Get list of folders
	status, folders = mail.list()
	if status != "OK":
		print("Failed to retrieve folders.")
		return all_folders

	for i, folder in enumerate(folders):
		decoded = folder.decode()
		match = re.search(r'"([^"]+)"$', decoded)
		if match:
			folder_name = match.group(1)
			all_folders.append(folder_name)
			all_folders.append("!")
		else:
			print(f"[{i}] (Could not parse) → {decoded}")
	return all_folders

def move_email(mail, msg, msg_id: str, target_folder: str):
    # Copy the message to the target folder
    copy_status, _ = mail.copy(msg_id, f'"{target_folder}"')
    if copy_status != 'OK':
        return [f"Failed to copy message {msg_id} to {target_folder}"]
        

    # Mark the original message as deleted
    mail.store(msg_id, '+FLAGS', '\\Deleted')
    mail.expunge()

    # Optional: Log subject or from_ for clarity
    subject = msg.get("Subject", "(No Subject)")
    sender = msg.get("From", "(Unknown Sender)")
    return [f" Moved '{subject}' from {sender} to '{target_folder}'"]

def has_attachment(msg):
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", "")).lower()
        if "attachment" in content_disposition:
            filename = part.get_filename()
            payload = part.get_payload(decode=True)
            if filename and payload:
                return (filename)
    return None

def save_attachment(attachment, output_path):
    """
    attachment: tuple of (filename, payload) from has_attachment()
    output_path: folder path to save the file into
    """
    filename, payload = attachment
    full_path = os.path.join(output_path, filename)

    with open(full_path, "wb") as f:
        f.write(payload)
    return [full_path]

		

def send(body, to, subject, file_paths):

	for recip in to:
		msg = EmailMessage()
		msg['Subject'] = subject
		msg['From'] = EMAIL_USER
		msg['To'] = recip

		service = "@" + EMAIL_USER.split("@", 1)[1]
		service = services[service].replace("imap", "smtp", 1 )
	
		body = "".join(body)
	
		msg.set_content(body)
	
		for file_path in file_paths:
			if not os.path.isfile(file_path):
				continue  # skip if not a file
			mime_type, _ = mimetypes.guess_type(file_path)
			mime_type = mime_type or 'application/octet-stream'
			maintype, subtype = mime_type.split('/', 1)
			with open(file_path, 'rb') as f:
				msg.add_attachment(
					f.read(),
					maintype=maintype,
					subtype=subtype,
					filename=os.path.basename(file_path)
				)
		try:
			with smtplib.SMTP(service, 587, timeout=10) as smtp:
				smtp.starttls()
				smtp.login(EMAIL_USER, EMAIL_PASS)
				smtp.send_message(msg)
		except Exception as e:
			return False, [f"Failed to send email: {e}"]
	return False, ["Email sent successfully."]


def download_attachments(mail, eid):
    mail.select(f'"{CURRENT_FOLDER}"')
    status, msg_data = mail.fetch(eid, "(RFC822)")
    if status != "OK":
        return [f"Failed to fetch message {eid}"]

    # Parse the message
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            # Prepare output directory
            home_dir = os.path.expanduser("~")
            out_dir = os.path.join(home_dir, eid)
            os.makedirs(out_dir, exist_ok=True)
            found = False
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", "")).lower()
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    payload = part.get_payload(decode=True)
                    if filename and payload:
                        filepath = os.path.join(out_dir, filename)
                        with open(filepath, "wb") as f:
                            f.write(payload)
                        found = True
            if found:
                return [f"Attachments saved to {out_dir}"]
            else:
                return [f"No attachments found in message {eid}"]
    return [f"Message {eid} not found or has no attachments"]