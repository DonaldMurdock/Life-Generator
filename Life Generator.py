#Donald Taylor
#Life Generator
#CS361
#Sprint 5 Assignment
#3/9/2021

import tkinter as tk
import csv
import sys
import os

class lg_GUI:
    def __init__(self, items, categories):
        """Creates a new GUI for the Life Generator. Requires lists of items and categories from
        the amazon data.
        """
        self.window = tk.Tk()

        self.items = items
        self.categories = categories

        self.cat_choice = None
        self.num_choice = None

        self.output_lines = []
        self.more_info_buttons = []
        self.more_infos = {}

    #Functions for displaying the GUI

    def launch_GUI(self):

        self.display_window()
        self.display_header()
        self.display_instructions()
        self.display_category_selection()
        self.display_number_selection()
        self.display_go_button()

        self.window.mainloop()

    def display_window(self):
        self.window.title("LIFE GENERATOR")
        self.window.geometry("1200x800")
        self.window.columnconfigure(0, minsize = 1200, weight=1)

    def display_header(self):
        header = tk.Label(text="LIFE GENERATOR")
        header.config(font = ('Arial Black', 40))
        header.grid(row=0, column=0, sticky = 'wn', pady = (0,10))

    def display_instructions(self):
        instructions_text = "Choose a category and number of results to see the most popular toys."
        instructions = tk.Label(text=instructions_text)
        instructions.grid(row=0,column=0, sticky = 'ws')

    def display_category_selection(self):
        cat_frame = tk.Frame(master=self.window)
        cat_frame.grid(row=1,column=0, sticky = 'w', pady = (20,0))

        cat_label = tk.Label(master = cat_frame, text = "Please select a category:")
        cat_label.pack(side = tk.LEFT)

        self.cat_choice = tk.StringVar(cat_frame)
        self.cat_choice.set(self.categories[0])

        cat_menu = tk.OptionMenu(cat_frame, self.cat_choice, *self.categories)
        cat_menu.pack(side = tk.LEFT)

    def display_number_selection(self):
        num_frame = tk.Frame(master=self.window)
        num_frame.grid(row=2,column=0, sticky = "w")

        num_label = tk.Label(master = num_frame, text = "How many would you like to see?")
        num_label.pack(side = tk.LEFT)

        Number = [1,5,10,15,20,25]

        self.num_choice = tk.StringVar(num_frame)
        self.num_choice.set(Number[0])

        num_menu = tk.OptionMenu(num_frame, self.num_choice, *Number)
        num_menu.pack(side = tk.LEFT)

    def display_go_button(self):
        button = tk.Button(self.window, text="GO!!!!!", command=self.display_results)
        button.grid(row=3, column=0, sticky="w")


    #Functions for clearing displayed content

    def clear_results(self):

        self.clear_items()
        self.clear_butons()
        self.clear_descriptions()

    def clear_items(self):
        for line in self.output_lines:
            line.destroy()

        self.output_lines.clear()

    def clear_butons(self):
        for button in self.more_info_buttons:
            button.destroy()

        self.more_info_buttons.clear()

    def clear_descriptions(self):
        for i in range(6, 56, 2):
            descriptions = self.window.grid_slaves(i,0)
            for description in descriptions:
                description.destroy()

    #functions for displaying content once the GO button is clicked

    def display_results(self):
        self.display_results_header()
        self.clear_results()

        user_input = self.get_user_input()
        results = calculate_results(self.items, user_input)

        self.generate_output(results)
        write_csv(results, user_input)

    def display_results_header(self):
        tabs = "\t" + "\t" + "\t"

        header_text = "\t" + "  Average Rating" + tabs + "  Number of Reviews" + tabs + "  Product Name"
        header = tk.Text(self.window, height = 1)
        header.grid(row=4, column=0, sticky='w')
        header.insert(tk.END, header_text)

    def get_user_input(self):
        """Gets the input from the GUI
        """
        user_input = {}
        user_input['input_item_type'] = 'toys'
        user_input['input_item_category'] = self.cat_choice.get().strip()
        user_input['input_number_to_generate'] =  int(self.num_choice.get())

        return user_input

    def generate_output(self, results):
        """displays the list of items along with 'More Info' Buttons"""
        cur_row = 5

        for item in results:
            text_and_button_frame = tk.Frame(master=self.window, width = 1200)
            text_and_button_frame.grid(row=cur_row, column=0, sticky='ew')

            self.create_more_info_button(text_and_button_frame)
            self.create_item_text(text_and_button_frame, item)

            #skipping rows by 2 to leave space for 'more info' descriptions
            cur_row += 2

        self.bind_buttons()

    def create_more_info_button(self, frame):
        button = tk.Button(master = frame, text = "More Info")
        button.pack(side=tk.LEFT)

        self.more_info_buttons.append(button)

    def create_item_text(self, frame, item):
        tabs = '\t' + '\t' + '\t'

        output_text = item['average_review_rating'] + tabs
        output_text += str(item['number_of_reviews']) + tabs + item['product_name']

        output = tk.Text(master = frame, wrap='none', height = 1, width = 1200)
        output.pack(side=tk.LEFT)
        output.insert(tk.END, output_text)

        self.output_lines.append(output)

    def bind_buttons(self):
        """Binds the 'More Info' buttons to the display_more_info function"""
        for i in range(len(self.more_info_buttons)):
            self.more_info_buttons[i].configure(command = lambda button_index = i: self.display_more_info(button_index))


    #Functions for displaying 'More Info'

    def display_more_info(self, button_index):

        self.convert_more_to_less(button_index)

        display_row = 2 * button_index + 6

        row_text = self.output_lines[button_index].get("1.0", tk.END)
        keyword1 = self.cat_choice.get().split()[0].lower()    #keyword1 is category
        keyword2 = row_text.split()[6].lower()                 #keyword2 is first word of item name

        info_text = self.get_info_from_content_generator(keyword1, keyword2)

        more_info = tk.Text(self.window, height = 5)
        more_info.grid(row=display_row, column=0, sticky='w')
        more_info.insert(tk.END, info_text)
        self.more_infos[str(display_row)] = more_info

    def convert_more_to_less(self, button_index):
        """When the 'more info' button is pressed it must be converted to a 'less info' button
        """
        current_button = self.more_info_buttons[button_index]
        current_button.configure(text = 'Less Info')
        current_button.configure(command = lambda : self.display_less_info(button_index))

    def display_less_info(self, button_index):
        display_row = 2 * button_index + 6
        self.more_infos[str(display_row)].destroy()

        self.convert_less_to_more(button_index)

    def convert_less_to_more(self, button_index):
        current_button = self.more_info_buttons[button_index]
        current_button.configure(text = 'More Info')

        current_button.configure(command = lambda : self.display_more_info(button_index))

    def get_info_from_content_generator(self, keyword1, keyword2):
        self.create_input_csv(keyword1, keyword2)

        command_line_string = "python content-generator.py CG-input.csv"
        os.system(command_line_string)

        CG_data = self.read_from_CG_output_csv()
        output = CG_data['ouput_content']

        return output

    def create_input_csv(self, keyword1, keyword2):
        """Creates csv called CG-input to be sent to content generator
        """
        keyword_entry = keyword1.strip() + ';' + keyword2.strip()

        with open("CG-input.csv", mode="w", encoding='utf-8') as output:
            output_writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # Header Row
            output_writer.writerow(["input_keywords"])

            # Keyword Entry
            print(keyword_entry)
            output_writer.writerow([keyword_entry])

    def read_from_CG_output_csv(self):
        """Gets the content back from the content generator in file called CG-output.csv
        """
        with open("CG-output.csv", mode="r", encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                CG_data = row

        return CG_data

#Functions for calculating results

def calculate_results(items, user_input):
    """Finds and sorts the results by the specifications and returns the top items in a list"""

    category = user_input['input_item_category']
    num_results = int(user_input['input_number_to_generate'])

    results = get_items_by_category(items, category)

    results.sort(key=sort_by_id)
    results.sort(reverse = True, key=sort_by_num_reviews)

    get_top(results, num_results * 10)

    results.sort(key=sort_by_id)
    results.sort(reverse=True, key=sort_by_rating)

    get_top(results, num_results)

    return results

def get_items_by_category(items, category):
    results = []

    for item in items:
        if item['amazon_category_and_sub_category'].rsplit(">")[0].strip() == category:
            results.append(item)

    return results

def sort_by_id(e):
    return e['uniq_id']

def sort_by_num_reviews(e):
    if e['number_of_reviews'] == '':
        return 0
    else:
        return int(float(e['number_of_reviews'].replace(",","")))

def sort_by_rating(e):
    return e['average_review_rating']

def get_top(results, num):
    """Takes a list 'results' and a number as parameters. Removes elements from the list until
    only the top 'num' remain. """

    for i in range(len(results) + 1):
        if i > num:
            results.pop()

#Functions for getting data from amazon
def get_all_items(data_file):
    """Reads CSV Data and returns a list containing all items. Each item is a dictionary.
    """
    with open(data_file, mode="r", encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        items = []

        for row in csv_reader:
            items.append(row)

    return items

def get_all_categories(items):
    """Gets list of categories for dropdown menu
    """
    categories = []

    for item in items:
        cur_category = item['amazon_category_and_sub_category'].rsplit(">")[0]
        if cur_category not in categories and cur_category != '':
            categories.append(cur_category)

    return categories

#Other functions
def write_csv(results, user_input):
    with open("LG-output.csv", mode="w", encoding='utf-8') as output:
        output_writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        #Header Row
        output_writer.writerow(["input_item_type",
                                "input_item_category",
                                "input_number_to_generate",
                                "output_item_name",
                                "output_item_rating",
                                "output_item_num_reviews",
                                "output_item_reviews"])

        #Results rows
        for item in results:
            output_writer.writerow([user_input['input_item_type'],
                                    user_input['input_item_category'],
                                    user_input['input_number_to_generate'],
                                    item['product_name'],
                                    item['average_review_rating'],
                                    str(item['number_of_reviews']),
                                    item['customer_reviews']])

def run_without_gui(input_filename, items):
    """Gets input from csv file and writes to output.csv
    """
    with open(input_filename, mode="r", encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            user_input = row

    results = calculate_results(items, user_input)

    write_csv(results, user_input)

def main():

    # Get all necessary data
    items = get_all_items("amazon_co-ecommerce_sample.csv")
    categories = get_all_categories(items)

    # If input CSV is provided as argument
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
        run_without_gui(input_filename, items)
    else:
        GUI = lg_GUI(items, categories)
        GUI.launch_GUI()

if __name__ == "__main__":
    main()