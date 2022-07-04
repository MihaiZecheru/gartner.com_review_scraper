import threading, time, os, subprocess
from CompanyReviews import CompanyReviews
from Review import Review
from tkinter import *
import tkinter.ttk as ttk

instructions = """
--------------------------------------------------------------------------------------------------------------------------------------------
1. Get a CSV file with the information from all the reviews on a vendor
--- OR ---
2. Get the information from a specific review on a vendor

To get all reviews as a csv:
  - Find a vendor you like on https://gartner.com
  - Get the URL of that vendor's reviews page. It should look like this:
    https://www.gartner.com/reviews/market/security-solutions-others/vendor/safebreach/product/safebreach-platform/
  - Enter that URL into the field below

To get a specific review:
  - Find a vendor you like on https://gartner.com
  - Find a review on that vendor
  - Get the URL of that review. It should look like this:
    https://www.gartner.com/reviews/market/security-solutions-others/vendor/safebreach/product/safebreach-platform/review/view/4294876
  - Enter that URL into the field below
--------------------------------------------------------------------------------------------------------------------------------------------
"""

class App(Tk):
  def __init__(self) -> None:
    super().__init__()
    self.font=("Helvetica", 20)
    self.bblue = "#3f78cc"

    # this selected attributes will change later, based on what the user selects
    self.selected_attributes = Review.attributes

    self.title("Gartner Web Scraper")
    self.geometry("600x600")
    self.configure(background=self.bblue)
    self.style = ttk.Style(self)
    self.style.theme_use("vista")
    self.initialize_components()

  def initialize_components(self):
    Button(self, text="Instructions", command=self.show_instructions, background="black", foreground="white", border=0, padx=50, font=self.font).pack(pady=(5, 20))
    Label(self, text="URL", background=self.bblue, foreground="black", font=self.font).pack()
    
    self.box = Entry(self, border=0, width=33, font=self.font)
    self.box.pack()
    self.box.focus()
    self.box.bind("<Return>", self.enter_event)

    self.error_frame = Frame(self, background=self.bblue)
    self.error_frame.pack(pady=5)


  def show_instructions(self):
    w = Toplevel(self)
    w.title("Instructions")
    w.geometry("753x300")
    _ = Label(w, text=instructions, background=self.bblue).pack()

  def enter_event(self, event=None):
    url = self.box.get()
    self.box.delete(0, END)

    if len(url) == 0: return

    # determine if url is for gartner.com
    if "/product/" not in url:
      self.show_invalid_url_error()
      return

    # determine if url is for a whole vendor or just one review
    mode = "review" if "/review/" in url else "vendor"
    
    if mode == "review":
      threading.Thread(daemon=True, target=self.show_review_to_screen, args=(int(url[url.index("/view/") + 6:]), url[url.index("/vendor/") + 8 : url.index("/product/")], url[url.index("/product/") + 9 : url.index("/review/")])).start()
    else:
      threading.Thread(daemon=True, target=self.show_scraping_results, args=(url,)).start()

  def show_review_to_screen(self, review_id: int, product_name_short: str, product_name_full: str):
    review = Review(review_id, product_name_short, product_name_full)
    self.displayed_attr_count = 0

    self.content_window = Toplevel(self)
    self.content_window.title("Request Response")
    self.geometry("1000x400")
    self.content_window.configure(background=self.bblue)

    self.content_frame = Frame(self.content_window, background=self.bblue)
    self.content_frame.pack()

    self.header_line = ""
    self.body_line = ""

    if "is_for" in self.selected_attributes:
      self.make_header_cell("Vendor")
      self.make_body_cell(review.is_for)
      self.displayed_attr_count += 1

    if "author_profile" in self.selected_attributes:
      self.make_header_cell("Author Profile")
      self.make_body_cell(review.author.profile)
      self.displayed_attr_count += 1

    if "author_industry" in self.selected_attributes:
      self.make_header_cell("Author Industry")
      self.make_body_cell(review.author.industry)
      self.displayed_attr_count += 1

    if "author_role" in self.selected_attributes:
      self.make_header_cell("Author Role")
      self.make_body_cell(review.author.role)
      self.displayed_attr_count += 1

    if "author_firm_size" in self.selected_attributes:
      self.make_header_cell("Author Firm Size")
      self.make_body_cell(review.author.firm_size)
      self.displayed_attr_count += 1

    if "author_deployment_architecture" in self.selected_attributes:
      self.make_header_cell("Deployment Architecture")
      self.make_body_cell(review.author.deployment_architecture)
      self.displayed_attr_count += 1

    if "url" in self.selected_attributes:
      self.make_header_cell("URL")
      self.make_body_cell(review.url)
      self.displayed_attr_count += 1

    if "comments" in self.selected_attributes:
      self.make_header_cell("Overall Comments")
      self.make_body_cell(review.comments)
      self.displayed_attr_count += 1

    if "like_most" in self.selected_attributes:
      self.make_header_cell("Like Most")
      self.make_body_cell(review.like_most)
      self.displayed_attr_count += 1

    if "dislike_most" in self.selected_attributes:
      self.make_header_cell("Dislike Most")
      self.make_body_cell(review.dislike_most)
      self.displayed_attr_count += 1

    if "rating" in self.selected_attributes:
      self.make_header_cell("Rating")
      self.make_body_cell(str(review.rating))
      self.displayed_attr_count += 1

    if "integration_and_deployment_rating" in self.selected_attributes:
      self.make_header_cell("Integration And Deployment Rating")
      self.make_body_cell(str(review.integration_and_deployment_rating))
      self.displayed_attr_count += 1

    if "services_and_support_rating" in self.selected_attributes:
      self.make_header_cell("Services And Support Rating")
      self.make_body_cell(str(review.services_and_support_rating))
      self.displayed_attr_count += 1

    if "product_capabilities_rating" in self.selected_attributes:
      self.make_header_cell("Product Capabilities Rating")
      self.make_body_cell(str(review.product_capabilities_rating))
      self.displayed_attr_count += 1 

    with open('{0}.csv'.format(f'{review.is_for}_review_{review_id}'.replace(" ", "_")), "w") as f:
      f.write(self.header_line[:-1] + '\n')
      f.write(self.body_line[:-1])

    Label(self.content_window, background=self.bblue, foreground="black", font=self.font, text="Click on the cell and copy the contents to read the whole thing\nOr click the button below to get the above table as a small csv file").pack(pady=(50, 0))
    Button(self.content_window, background="black", font=self.font, foreground="white", text="View In File", command=lambda event=None: App.view_csv_in_file(self, event=event)).pack(pady=(0, 25))

  def show_invalid_url_error(self):                                                                                     # red
    self.invalid_url_error_label = Label(self.error_frame, text="Invalid URL. Refer to the instructions for help.", background=self.bblue, foreground="#750c0c", font=self.font)
    self.invalid_url_error_label.grid(row=0, column=0)
    self.delete_label_timer()

  def delete_label_timer(self):
    threading.Thread(daemon=True, target=lambda: [time.sleep(2.5), self.invalid_url_error_label.destroy()]).start()

  def make_header_cell(self, text: str) -> None:
    header_cell = Entry(self.content_frame, background="black", foreground="white", borderwidth=0, justify="center")
    header_cell.grid(row=0, column=self.displayed_attr_count, padx=2, pady=1)
    header_cell.insert(0, text)
    self.header_line += f"{text},"

  def make_body_cell(self, text: str) -> None:
    body_cell = Entry(self.content_frame, background="black", foreground="white", borderwidth=0, justify="center")
    body_cell.grid(row=1, column=self.displayed_attr_count, padx=2, pady=1)
    body_cell.insert(0, text)
    self.body_line += f"{text},"

  def view_csv_in_file(self, event=None) -> None:
    subprocess.Popen(f'explorer "{os.path.normpath(os.getcwd())}"')
  
  def show_scraping_results(self, url: str) -> None:
    self.waiting_window = Toplevel(self)
    try:
      self.waiting_window.title("Waiting...")
      self.waiting_window.geometry("800x200")
      self.waiting_window.config(background=self.bblue)

      Label(self.waiting_window, background=self.bblue, foreground="black", font=self.font, text="The data is being collected for you...").pack()
      self.progress_bar = ttk.Progressbar(master=self.waiting_window, orient=HORIZONTAL, mode="determinate", maximum=100, value=0)
      self.progress_bar.pack()
      self.progress_bar['value'] = 0
    except: pass

    company_reviews = CompanyReviews(url, csv_attributes=self.selected_attributes, app=self)

    try:
      self.progress_bar.stop()
      self.waiting_window.destroy()
    except: pass

    try: company_reviews.file.close()
    except: pass

    try:
      self.nwindow = Toplevel(self)
      self.nwindow.title("Scraping Results")
      self.nwindow.geometry("1200x200")
      self.nwindow.config(background=self.bblue)

      Label(self.nwindow, wraplength=1100, background=self.bblue, foreground="black", font=self.font, text='Your file is ready. The name of the file is "{0}"\nWould you like to go there now?'.format(company_reviews.file_name[3:])).pack()
      Button(self.nwindow, background="black", foreground="white", text="Take Me There", font=self.font, command=lambda event=None: self.view_csv_in_file(self)).pack()
    except: pass

  def increment_progress_bar(self, amount: int) -> None:
    try:
      self.progress_bar['value'] += amount
      self.waiting_window.update()
    except: pass


if __name__ == '__main__':
  App().mainloop()