#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
GRIFFEYE-CRAWLER CLI
--------------------
(c) 2023, Luzerner Polizei
Author:  Michael Wicki
Version: 0.1
"""
version = "v0.1"

import argparse

import os
import sys
import json
import traceback
from datetime import datetime
# docx...
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_ALIGN_VERTICAL



class Device:
    def __init__(self, sourceid, category, initial_date):
        self.sourceid = sourceid
        self.categories = { category: Category(category, initial_date) }
        self.legal_count = 0
        self.illegal_count = 0

    def add_date(self, category, date):
        if category not in self.categories.keys():
            self.categories[category] = Category(category, date)
        else:
            self.categories[category].add_date(date)

    def add_file(self, category, path, mediatype, date, hash):
        self.categories[category].add_file(path, mediatype, date, hash)
        
        # increase legal/illegal count
        if category_legality.get(category, True):
            self.legal_count += 1
        else:
            self.illegal_count += 1

    def get_sourceid(self):
        return self.sourceid

    def get_categories(self):
        return self.categories

    def get_category(self, category):
        if category not in self.categories.keys():
            return None
        else:
            return self.categories[category]

    def get_counts(self):
        """
        returns a tuple with total count, legal count & illegal count of the device
        """
        return (self.legal_count+self.illegal_count, self.legal_count, self.illegal_count)


class Category:
    def __init__(self, name, initial_date):
        self.name = name
        self.legality = category_legality.get(name, True)
        self.min_date = empty_date
        if initial_date != unix_date:
            self.min_date = initial_date
        self.max_date = initial_date
        self.date_groups = {}
        self.pic_count = 0
        self.vid_count = 0
        self.tot_count = 0
        self.paths = {}
        self.cachepaths = {}
        self.cachegroups = {}
        self.pic_hashes = set()
        self.vid_hashes = set()

    def add_date(self, date):
        if date != empty_date and date != unix_date:
            if self.min_date == empty_date or date < self.min_date:
                self.min_date = date
            if self.max_date == empty_date or date > self.max_date:
                self.max_date = date

    def add_file(self, path, mediatype, date, hash):
        # increase counters & add hash to 'hashes' (>> deduplicates itself)
        self.tot_count += 1
        if mediatype == "Image":
            self.pic_count += 1
            self.pic_hashes.add(hash)
        if mediatype == "Video":
            self.vid_count += 1
            self.vid_hashes.add(hash)

        # increase path
        self.increase_path(path)

        # increase date
        self.increase_date(date)

    def merge(self, merge_cat):
        # merge daterange
        self.add_date(merge_cat.min_date)
        self.add_date(merge_cat.max_date)
        # merge counts
        self.tot_count += merge_cat.get_counts()[0]
        self.pic_count += merge_cat.get_counts()[1]
        self.vid_count += merge_cat.get_counts()[2]
        # merge dategroups
        for item in merge_cat.date_groups.items():
            key = item[0]
            value = item[1]
            if key not in self.date_groups.keys():
                self.date_groups[key] = value  # create
            else:
                self.date_groups[key] += value # increase
        # merge paths
        for path in merge_cat.paths.keys():
            if path not in self.paths.keys():
                self.paths[path] = 1    # create
            else:
                self.paths[path] += 1   # increase
        # merge cachepaths
        for path in merge_cat.cachepaths.keys():
            group = self.get_cache_group(path)
            if group is not None:
                if group not in self.cachegroups.keys():
                    self.cachegroups[group] = merge_cat.cachepaths[path]    # create
                else:
                    self.cachegroups[group] += merge_cat.cachepaths[path]     # increase
        # merge hashes
        self.pic_hashes.update(merge_cat.get_pic_hashset())
        self.vid_hashes.update(merge_cat.get_vid_hashset())

    def get_cache_group(self, path):
        for k in known_cache_paths.keys():
            if k in path:
                return known_cache_paths[k]
        return None
    
    def increase_path(self, path):
        if path in self.cachepaths.keys():
            # path is in cachepath >> increase count
            self.cachepaths[path] += 1
            self.cachegroups[self.get_cache_group(path)] += 1
        else:
            # path NOT in cachepath >> check for cache
            group = self.get_cache_group(path)
            if group is not None:
                # path is cache
                self.cachepaths[path] = 1 # create
                if group not in self.cachegroups.keys():
                    self.cachegroups[group] = 1    # create
                else:
                    self.cachegroups[group] += 1   # increase
            else:
                # path is NOT cache
                if path not in self.paths.keys():
                    self.paths[path] = 1    # create
                else:
                    self.paths[path] += 1   # increase

    def increase_date(self, date):
        year = int(date[6:10])
        if year == 1 or year == 1970: # no date or unix date
            year = 9999
        if year not in self.date_groups.keys():
            self.date_groups[year] = 1  # create
        else:
            self.date_groups[year] += 1 # increase

    def get_date_range(self):
        if self.min_date == empty_date or self.max_date == empty_date:
            return "undefiniert"
        return self.min_date.strftime("%d.%m.%Y")+" - "+self.max_date.strftime("%d.%m.%Y")

    def get_date_range_days(self):
        return (self.max_date - self.min_date).days + 1

    def get_pic_hashset(self):
        return self.pic_hashes

    def get_vid_hashset(self):
        return self.vid_hashes

    def get_unique_counts(self):
        """
        returns a tuple with total count, picture count & video count of binary unique files (based on the hash)
        """
        return (len(self.pic_hashes.union(self.vid_hashes)), len(self.pic_hashes), len(self.vid_hashes))

    def get_counts(self):
        """
        returns a tuple with total count, picture count & video count of the category
        """
        return (self.tot_count, self.pic_count, self.vid_count)
    
    def get_counts_string(self):
        """
        returns a string with formatted picture- & videos-count
        """
        result = ""
        # pictures
        if self.pic_count > 0:
            result += "{} ".format(self.pic_count)
            if self.pic_count > 1:
                result += "Bilder"
            else:
                result += "Bild"
            # binary unique
            result += " ({})".format(len(self.pic_hashes))
            if self.vid_count > 0:
                result += ", "
        # videos
        if self.vid_count > 0:
            result += "{} ".format(self.vid_count)
            if self.vid_count > 1:
                result += "Videos"
            else:
                result += "Video"
            # binary unique
            result += " ({})".format(len(self.vid_hashes))
        return result

    def get_grouped_dates(self):
        """
        returns a string with the percentage of illegal files per year
        """
        result = ""
        for year in sorted(self.date_groups.keys()):
            # calculate percentage of total files
            perc = (self.date_groups[year]/self.tot_count)*100
            if year == 9999:
                year = "undef."
            perc_str = "{:.0f}%".format(perc)
            if round(perc, 0) == 0 and perc > 0:
                perc_str = "<1%"
            result = result+"{}: {}, ".format(year, perc_str)
        return result[:-2] # kill last ', '

    def get_browsercache_total(self):
        sum = 0
        for c in self.cachegroups.keys():
            if c in browser_names:
                sum += self.cachegroups[c]
        return sum

    def get_browsercache_sums(self):
        """
        returns a dict with counts (value) for the specific browsers (key)
        """
        result = {}
        for c in self.cachegroups.keys():
            if c in browser_names:
                result[c] = self.cachegroups[c]
        return result

    def get_thumbcache_sum(self):
        sum = 0
        for c in self.cachegroups.keys():
            if c in thumbcache_names:
                sum += self.cachegroups[c]
        return sum


class PathNotFoundException(Exception):
    """
    error in case of a path not found
    """
    def __init__(self, path):
        self.message = f"Path '{path}' not found"

class ColumnNotFoundException(Exception):
    """
    error in case of a column name not found
    """
    def __init__(self, columnname):
        self.message = f"Column '{columnname}' not found"

class SeparatorNotFoundException(Exception):
    """
    error in case of the column separator could not be detected
    """
    def __init__(self):
        self.message = f"Column separator could not be found... Please use option -s"

class LineNotValidException(Exception):
    """
    error in case of a csv-entry with ; in a field without " around it
    """
    def __init__(self, linenumber):
        self.message = f"Line '{linenumber}' is not valid"



def configure_argparse():
    global args
    parser = argparse.ArgumentParser(prog="gc-cli", description="CLI-Version of 'GriffeyeCrawler' - Analyze an exported filelist of Griffeye", formatter_class=argparse.RawTextHelpFormatter)
    parser.version=version
    parser.add_argument("file", type=str, help="export csv of Griffeye")    
    parser.add_argument("-v", "--version", action="version")
    parser.add_argument("-o", metavar="output", action="store", type=str, 
                        help='''\
defines the output path/filename
could be only a path (has to end with a path separator) or can also include a filename
(default: input directory and input filename with the extension of the format)
defines the format too based on the file extension and overwrites -f''')
    parser.add_argument("-f", metavar="format", action="store", type=str, 
                        help=f'''\
defines the output format.
possible values: {", ".join(map(str,valid_formats))} (default: {default_format})''')
    parser.add_argument("--date", metavar="dates", action="store", type=str, 
                        help='''\
list of datefields separated by comma to get the dates from
(default: created date,last write time)''')
    parser.add_argument("-n", metavar="number", action="store", type=int, help="number of paths to show per category")
    parser.add_argument("-s", metavar="separator", action="store", type=str, 
                        help='''\
defines the column separator
(default: automatically detects the separators used by griffeye > comma or semicolon)''')
    parser.add_argument("--nodetails", action="store_true", help="don't generate the pathdetails file")
    args = parser.parse_args()

def progress(count, total, status=''):
    """
    handling of the progressbar
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def get_linecount(filename):
    """
    count total lines for progressbars
    """
    counter = -1
    file_input = open(filename, "r", encoding=input_encoding)
    for line in file_input:
        counter += 1
        if counter == 0:
            continue
    file_input.close()
    return counter

def get_titlestring(title, symbol="-", length=70):
    """
    creates a titleline with centered text
    """
    half_length = (length//2)-1  # including blank
    half_title = (len(title)//2)-1  # including blank
    symbol_count = half_length-half_title
    addition = ""
    if half_title%2 > 0 or half_length%2 > 0:
        addition = symbol
    return symbol*symbol_count+" "+title+" "+symbol*symbol_count+addition

def get_browser_percent(browser_count, total_count):
    perc = (browser_count/total_count)*100
    if round(perc, 0) == 0 and perc > 0:
        return "<1%"
    return "{:.0f}%".format(perc)

def shorten_path(path):
    """
    shortens the filepath by the first two directories
    """
    first = path[path.find(os.path.sep)+1:]
    return first[first.find(os.path.sep)+1:]

def detect_separator(header):
    """
    detect the csv separator (, or ;)
    """
    global csv_separator
    if header.find(',') > -1:
        csv_separator = ","
    elif header.find(';') > -1:
        csv_separator = ";"
    else:
        raise SeparatorNotFoundException()

def get_date_field(data):
    for i in column_index.keys():
        if not i.startswith("col_date"):
            continue

        # if field is empty () or date is empty (01.01.0001) try the next date
        if len(data[column_index[i]].strip()) > 0 and data[column_index[i]] != empty_date_string:
            return data[column_index[i]]
    return empty_date_string

def check_columns(header):
    """
    check for needed columns & fill columnindex-dictionary for column access with columnname
    """
    cols = header[:-1].split(csv_separator)
    for c in config["needed_columns"]:
        # ignore datefield > checked with datefields_list
        if c["key"]=="col_date":
            continue

        if c["columnname"] in cols:
            # column in csv found
            column_index[c["key"]] = cols.index(c["columnname"])
        elif "alt" in c and c["alt"] in cols:
            # column has 'alt'-entry in config and 'alt' is found in csv
            column_index[c["key"]] = cols.index(c["alt"])
        else:
            # column and 'alt' in csv not found
            raise ColumnNotFoundException(c["columnname"])

    # check for datefields
    counter = 0
    for d in datefields_list:
        if d in cols:
            column_index["col_date"+str(counter)] = cols.index(d)
            counter+=1
        else:
            raise ColumnNotFoundException(d)

def convert_line(line, linenumber):
    result = []
    while line.find('"') > -1:
        # cut out field with separator in it
        pos_start = line.find('"')+1
        while True:
            pos_end = line.find('"', pos_start)
            if pos_start == pos_end:
                pos_start += 1
                continue
            break
        if pos_start == 0 or pos_end == -1:
            raise LineNotValidException(linenumber)
        field = line[pos_start:pos_end]
        # get range before and after the field
        second_part = line[pos_end+2:-1]   # +1 = ", +1 = separator, -1 = general
        if pos_start > 2:
            first_part = line[:pos_start-2]  # -1 = ", -1 = general 
            # add first part to result_list
            result = result + first_part.split(csv_separator) + [field]
        else:
            # add field to result_list
            result = result + [field]

        # cut first part of line
        line = second_part
    result = result + second_part.split(csv_separator)
    return result

def analyze_file(filename):
    """
    - check for needed columns & fill columnindex-dictionary
    - collect devices & fill devicelist
    - detect min & max date for daterange (per device)
    """
    counter = -1
    file_input = open(filename, "r", encoding=input_encoding)
    for line in file_input:
        counter += 1
        if counter == 0:
            # csv-header...
            line = line.replace("\ufeff", "")
            if not args.s:
                detect_separator(line)
            check_columns(line)
            global column_count
            column_count = line.count(csv_separator)
            continue

        # csv-entry...
        # get device & date from csv
        try:
            if line.count(csv_separator) != column_count:
                data = convert_line(line, counter+1)
            else:
                data = line.split(csv_separator)
            data_category = data[column_index['col_category']]
            data_date = get_date_field(data)
            current_date = datetime.strptime(data_date[0:10], "%d.%m.%Y")
            data_device = data[column_index['col_device']]
            # check for device or create it when needed
            if data_device not in devices.keys():
                devices[data_device] = Device(data_device, data_category, current_date)
            else:
                devices[data_device].add_date(data_category, current_date)
        except LineNotValidException as exp:
            invalid_lines.append(exp.args[0])
        # update progressbar
        progress(counter, line_count)

    file_input.close()
    return counter

def process_file():
    file_input = open(input_filename, "r", encoding=input_encoding)
    counter = -1
    for line in file_input:
        counter += 1
        # ignore csv-header
        if counter == 0:
            continue

        # get data from file
        try:
            if line.count(csv_separator) != column_count:
                column = convert_line(line, counter+1)
            else:
                column = line.split(csv_separator)
            data_category = column[column_index['col_category']]
            data_path = column[column_index['col_path']]
            data_type = column[column_index['col_type']]
            data_date = get_date_field(column)
            data_device = column[column_index['col_device']]
            data_hash = column[column_index['col_hash']]
            # add data to device
            device = devices[data_device]
            device.add_file(data_category, data_path, data_type, data_date, data_hash)
        except LineNotValidException as exp:
            pass
        # update progressbar
        progress(counter, line_count)
    file_input.close()
    return counter

def calculate_device_totals():
    """
    calculates totals from devices
    """
    global device_totals
    global cat_devcount
    for d in devices:
        categories = devices[d].get_categories()
        for dev_cat in categories.values():
            # increase/generate devicecount for category
            if dev_cat.name not in cat_devcount.keys():
                cat_devcount[dev_cat.name] = 1
            else:
                cat_devcount[dev_cat.name] += 1
            # get/generate total category
            total_cat = None
            if dev_cat.name not in device_totals.keys():
                total_cat = Category(dev_cat.name, dev_cat.min_date)
                device_totals[dev_cat.name] = total_cat
            else:
                total_cat = device_totals[dev_cat.name]
            # merge device-category to total-category
            total_cat.merge(dev_cat)

def write_outputfile_docx():
    text_fontname = "Arial"
    text_fontsize = Pt(11)
    table_fontsize = Pt(8)
    table_rowheight = Pt(14)

    document = Document()
    # write results of file-analysis
    document.add_heading(f"GRIFFEYE-CRAWLER - Results from {datetime.now().strftime('%d.%m.%Y')}", 1)
    p = document.add_paragraph()
    run = p.add_run(f"Analyzed File:\t{input_filename}\nNumber of rows:\t{line_count}")
    run.font.name = text_fontname
    run.font.size = text_fontsize
    counter = 0
    totallength = len(devices)+1 # + total-table

    # write total results
    document.add_heading("Total over all devices", 2)
    for c in sorted(category_sort.keys()):
        if category_sort[c] not in device_totals.keys():
            continue
        cat = device_totals[category_sort[c]]
        # write table...
        table = document.add_table(rows=1, cols=2, style="Table Grid")
        # format header
        hdr_cells = table.rows[0].cells
        # cell merging
        hdr_cells[0].text = cat.name
        datentr = "Disk"
        if cat_devcount[category_sort[c]] > 1:
            datentr = "Disks"
        hdr_cells[1].text = f"{cat.get_counts_string()} on {cat_devcount[category_sort[c]]} {datentr}"
        # background color
        cellshade = OxmlElement("w:shd")
        cellshade.set(qn("w:fill"), "#CCCCCC")
        cellprop = hdr_cells[0]._tc.get_or_add_tcPr()
        cellprop.append(cellshade)
        cellshade = OxmlElement("w:shd")
        cellshade.set(qn("w:fill"), "#CCCCCC")
        cellprop = hdr_cells[1]._tc.get_or_add_tcPr()
        cellprop.append(cellshade)
        # row alignment
        table.rows[0].height = table_rowheight
        hdr_cells[0].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        hdr_cells[1].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        # font
        run = hdr_cells[0].paragraphs[0].runs[0]
        run.font.name = text_fontname
        run.font.size = table_fontsize
        run.font.bold = True
        run = hdr_cells[1].paragraphs[0].runs[0]
        run.font.name = text_fontname
        run.font.size = table_fontsize

        # fill data...
        if category_sort[c] != "Legale Pornographie":
            # timeline
            row_cells = table.add_row().cells
            row_cells[0].text = "istribution in time period:"
            row_cells[1].text = f"{cat.get_grouped_dates()}"
            # proportion storage <-> browser cache
            row_cells = table.add_row().cells
            row_cells[0].text = "Percentage Browsercache:"
            row_cells[1].text = f"{get_browser_percent(cat.get_browsercache_total(), cat.get_counts()[0])}"
        
        # format table
        for row in table.rows[1:]:
            i=-1
            row.height = table_rowheight
            for cell in row.cells:
                i+=1
                # cell alignment
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                # font
                run = cell.paragraphs[0].runs[0]
                run.font.name = text_fontname
                run.font.size = table_fontsize
                if i == 0:
                    # name-column bold
                    run.font.bold = True
        document.add_paragraph().paragraph_format.space_after = Pt(0)

    counter += 1
    # update progressbar
    progress(counter, totallength)

    # write results of devices
    for d in devices:
        counter += 1
        document.add_heading(d, 2)
        for c in sorted(category_sort.keys()):
            if category_sort[c] not in devices[d].categories:
                continue

            cat = devices[d].get_category(category_sort[c])
            # write table...
            table = document.add_table(rows=1, cols=2, style="Table Grid")
            # format header
            hdr_cells = table.rows[0].cells
            # cell merging
            hdr_cells[0].merge(hdr_cells[1])
            hdr_cells[0].text = cat.name
            # background color
            cellprop = hdr_cells[0]._tc.get_or_add_tcPr()
            cellshade = OxmlElement("w:shd")
            cellshade.set(qn("w:fill"), "#CCCCCC")
            cellprop.append(cellshade)
            # row alignment
            table.rows[0].height = table_rowheight
            hdr_cells[0].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            # font
            run = hdr_cells[0].paragraphs[0].runs[0]
            run.font.name = text_fontname
            run.font.size = table_fontsize
            run.font.bold = True

            # fill data...
            # count & mediatype
            row_cells = table.add_row().cells
            row_cells[0].text = "Quantity/Filetype:"
            row_cells[1].text = cat.get_counts_string()
            if category_sort[c] != "Legale Pornographie":
                # daterange
                row_cells = table.add_row().cells
                row_cells[0].text = "Creation on disk:"
                row_cells[1].text = f"{cat.get_date_range()}"
                # timeline
                row_cells = table.add_row().cells
                row_cells[0].text = "istribution in time period:"
                row_cells[1].text = f"{cat.get_grouped_dates()}"
                # proportion storage <-> browser cache
                row_cells = table.add_row().cells
                row_cells[0].text = "Percentage Browsercache:"
                row_cells[1].text = f"{get_browser_percent(cat.get_browsercache_total(), cat.get_counts()[0])}"
                # paths
                row_cells = table.add_row().cells
                row_cells[0].text = "Most common locations:"
                # show top-paths
                rows = ""
                i = 0
                # copy the pathlist and add a thumbcache- and browsercache-entries with the total sums to the temporary copy
                temppaths = dict(cat.paths)
                thumbsum = cat.get_thumbcache_sum()
                if thumbsum > 0:
                    temppaths[name_for_thumbcache] = thumbsum
                browser_sums = cat.get_browsercache_sums()
                for b in browser_sums.keys():
                    temppaths[name_for_browsercache+" "+b] = browser_sums[b]

                # work with the temporary pathlist incl. the thumbcache-entry
                for k in sorted(temppaths, key=temppaths.get, reverse=True):
                    i += 1
                    if i > number_of_showed_paths:
                        break
                    if i > 1:
                        rows += "\n"
                    rows += f"- {shorten_path(k)}"
                row_cells[1].text = rows
            
            # format table
            for row in table.rows[1:]:
                i=-1
                row.height = table_rowheight
                for cell in row.cells:
                    i+=1
                    # cell alignment
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    # font
                    run = cell.paragraphs[0].runs[0]
                    run.font.name = text_fontname
                    run.font.size = table_fontsize
                    if i == 0:
                        # name-column bold
                        run.font.bold = True
            document.add_paragraph().paragraph_format.space_after = Pt(0)

        progress(counter, totallength)
        document.save(result_filename)

def write_outputfile_json():
    pass

def write_outputfile_txt():
    file_result = open(result_filename,"w", encoding=result_encoding)
    # write results of file-analysis
    file_result.write(f"GRIFFEYE-CRAWLER - results from {datetime.now().strftime('%d.%m.%Y')}\n")
    file_result.write("="*43+"\n")
    file_result.write(f"Analyzed File:\t{input_filename}\n")
    file_result.write(f"Number of Rows:\t{line_count}\n")
    file_result.write("\n")
    counter = 0
    totallength = len(devices)+1 # + total-table

    # write total results
    file_result.write("\n{}\n".format(get_titlestring("Total over all devices", "=")))
    for c in sorted(category_sort.keys()):
        if category_sort[c] not in device_totals.keys():
            continue
        cat = device_totals[category_sort[c]]
        file_result.write("\n{}\n".format(get_titlestring(cat.name, "\u0387")))
        # count & mediatype
        file_result.write(f"Quantity/Filetype:\t\t\t\t{cat.get_counts_string()}\n")
        # devicecount
        file_result.write(f"Number of devices:\t\t\t\t{cat_devcount[category_sort[c]]}\n")
        if category_sort[c] != "Legale Pornographie":
            # daterange
            file_result.write(f"Creation on disk:\t\t\t\t{cat.get_date_range()}\n")
            # timeline
            file_result.write(f"Distribution in time period:\t{cat.get_grouped_dates()}\n")
            # proportion storage <-> browser cache
            file_result.write(f"Percentage Browsercache:\t\t{get_browser_percent(cat.get_browsercache_total(), cat.get_counts()[0])}\n")
    file_result.write("\n")

    counter += 1
    # update progressbar
    progress(counter, totallength)

    # write results of devices
    for d in devices:
        counter += 1
        file_result.write("\n{}\n".format(get_titlestring(d, "=")))
        for c in sorted(category_sort.keys()):
            if category_sort[c] not in devices[d].categories:
                continue

            cat = devices[d].get_category(category_sort[c])
            file_result.write("\n{}\n".format(get_titlestring(cat.name, "\u0387")))
            # count & mediatype
            file_result.write(f"Menge/Dateityp:\t\t\t\t{cat.get_counts_string()}\n")
            if category_sort[c] != "Legale Pornographie":
                # daterange
                file_result.write(f"Creation on disk:\t\t\t\t{cat.get_date_range()}\n")
                # timeline
                file_result.write(f"Distribution in time period:\t{cat.get_grouped_dates()}\n")
                # proportion storage <-> browser cache
                file_result.write(f"Percentage Browsercache:\t\t{get_browser_percent(cat.get_browsercache_total(), cat.get_counts()[0])}\n")
                # paths
                file_result.write("Most common Locations:\n")
                # show top-paths
                i = 0
                # copy the pathlist and add a thumbcache- and browsercache-entries with the total sums to the temporary copy
                temppaths = dict(cat.paths)
                thumbsum = cat.get_thumbcache_sum()
                if thumbsum > 0:
                    temppaths[name_for_thumbcache] = thumbsum
                browser_sums = cat.get_browsercache_sums()
                for b in browser_sums.keys():
                    temppaths[name_for_browsercache+" "+b] = browser_sums[b]

                # work with the temporary pathlist incl. the thumbcache-entry
                for k in sorted(temppaths, key=temppaths.get, reverse=True):
                    i += 1
                    if i > number_of_showed_paths:
                        break
                    file_result.write(f"- {shorten_path(k)}\n")

        file_result.write("\n")
        # update progressbar
        progress(counter, totallength)

    file_result.close()

def write_pathdetails():
    """
    creates the outputfile (txt) with detailed information
    """
    details_name = config["result"]["pathdetails_name"]
    if not details_name.endswith(".txt"):
        details_name = details_name+".txt"
    details_name = f"{get_file_basename(get_output_name(input_filename))}_{details_name}"
    enc = config["result"]["pathdetails_encoding"]
    file_result = open(get_output_path(input_filename)+details_name,"w", encoding=enc)
    # write results of file-analyze
    file_result.write(f"GRIFFEYE-CRAWLER - path details from {datetime.now().strftime('%d.%m.%Y')}\n")
    file_result.write("="*47+"\n")
    file_result.write(f"Analyzed File:\t{input_filename}\n")
    file_result.write(f"Number of Rows:\t{line_count}\n")
    file_result.write("\n")

    # write results of devices
    counter = 0
    for d in devices:
        counter += 1
        file_result.write("\n{}\n".format(get_titlestring(d, "=")))
        file_result.write("{} Files (Legal: {}, Illegal: {})".format(devices[d].get_counts()[0], devices[d].get_counts()[1], devices[d].get_counts()[2]))
        file_result.write("  >>  {:.2f}% illegal\n".format((devices[d].get_counts()[2]/devices[d].get_counts()[0])*100))
        for c in sorted(category_sort.keys()):
            if category_sort[c] not in devices[d].categories:
                continue

            cat = devices[d].get_category(category_sort[c])
            file_result.write("\n{}\n".format(get_titlestring(cat.name, "\u0387")))
            # count & mediatype
            file_result.write(f"Quantity/Filetype:\t\t\t\t{cat.get_counts_string()}\n")
            # daterange
            file_result.write(f"Creation on disk:\t\t\t\t{cat.get_date_range()}\n")
            # timeline
            file_result.write(f"Distribution in time period:\t{cat.get_grouped_dates()}\n")
            # proportion storage <-> browser cache
            browser_total = cat.get_browsercache_total()
            counts_total = cat.get_counts()[0]
            perc = (browser_total/counts_total)*100
            perc_str = "{:.0f}%".format(perc)
            if round(perc, 0) == 0 and perc > 0:
                perc_str = "<1%"
            file_result.write(f"Percentage browsercache:\t\t{perc_str} >>> (Total: {counts_total}, Browsercache: {browser_total})\n")
            # paths
            file_result.write("Locations:\n")

            # show paths
            # copy the pathlist and add a thumbcache-entry with the total sum to the temporary copy
            temppaths = dict(cat.paths)
            thumbsum = cat.get_thumbcache_sum()
            if thumbsum > 0:
                temppaths[name_for_thumbcache] = thumbsum
            # work with the temporary pathlist incl. the thumbcache-entry
            for k in sorted(temppaths, key=temppaths.get, reverse=True):
                file_result.write("- {} >>> {}\n".format(k, str(temppaths[k])))
            # if available, write other caches
            if len(cat.cachepaths)>0:
                file_result.write("    > Caches <\n")
                for k in sorted(cat.cachegroups, key=cat.cachegroups.get, reverse=True):
                    file_result.write("- {} >>> {}\n".format(k, str(cat.cachegroups[k])))
                file_result.write("    > Cache-Details <\n")
                for k in sorted(cat.cachepaths, key=cat.cachepaths.get, reverse=True):
                    file_result.write("- {} >>> {}\n".format(k, str(cat.cachepaths[k])))

        file_result.write("\n")
        # update progressbar
        progress(counter, len(devices))

    file_result.close()

def read_config():
    """
    read configurations (can be overwritten by input options)
    """
    global config
    global input_encoding
    global result_encoding
    global category_legality
    global category_sort
    global known_cache_paths
    global browser_names
    global thumbcache_names
    global number_of_showed_paths

    with open('config.json') as c:
        data = c.read()
    config = json.loads(data)
    input_encoding = config["input"]["encoding"]
    result_encoding = config["result"]["encoding"]
    for cat in config["categories"]:
        category_legality[cat["name"]] = cat["legality"]
        category_sort[cat["sort"]] = cat["name"]
    for cac in config["caches"]:
        known_cache_paths[cac["path"]] = cac["name"]
        if cac["is_browser"] and cac["name"] not in browser_names:
            browser_names.append(cac["name"])
        if cac["is_thumbcache"] and cac["name"] not in thumbcache_names:
            thumbcache_names.append(cac["name"])
    number_of_showed_paths = config["result"]["number_of_showed_paths"]

def generate_datefields_list():
    global datefields_list
    if args.date:
        datefields_list = args.date.split(",")
            
    if not datefields_list:
        if args.date:
            print(f"No date definitions found! Default is used...")
        for c in config["needed_columns"]:
            if c["key"]=="col_date":
                datefields_list.append(c["columnname"])
                break
        datefields_list.append(config["other"]["alternative_date_column"])

def get_file_basename(input):
    filename = os.path.basename(input)
    return os.path.splitext(filename)[0]

def get_output_format():
    ext = ""
    if args.o and not args.o.endswith(os.sep):
        ext = os.path.splittext(args.o)[1]
    elif args.f:
        ext = args.f
    else:
        ext = default_format
    
    # check extension
    if ext in valid_formats:
        return ext
    
    print(f"Output format '{ext}' not found! Default format is used...")
    return default_format

def get_output_name(inputname):
    if args.o and not args.o.endswith(os.path):
        return f"{get_file_basename(args.o)}.{get_output_format()}"
    return f"{get_file_basename(inputname)}.{get_output_format()}"

def get_output_path(inputname):
    path = ""
    if args.o:
        if args.o.endswith(os.sep):
            path = args.o
        else:
            path = os.path.dirname(args.o)
    else:
        path = os.path.dirname(inputname)

    # check for existance
    if path != "" and not os.path.exists(path):
        raise PathNotFoundException(path)
    if path != "":
        path = path+os.sep
    return path



# init
column_index = {}
devices = {}
device_totals = {}
cat_devcount = {}
invalid_lines = []
datefields_list = []
csv_separator = ""
column_count = 0
line_count = 0

default_format = "docx"
valid_formats = ["docx", "json", "txt"]

empty_date = datetime.strptime("01.01.0001", "%d.%m.%Y")
empty_date_string = "01.01.0001 00:00:00"
unix_date = datetime.strptime("01.01.1970", "%d.%m.%Y")

# init configs
config = {}
input_encoding = ""
result_filename = ""
result_encoding = ""
category_legality = {}
category_sort = {}
known_cache_paths = {}
browser_names = []
thumbcache_names = []
number_of_showed_paths = 0

# init argparse
args = None
configure_argparse()

try:
    read_config()
    input_filename = args.file
    # remove " & ' from path (prevents error while reading the file)
    input_filename = input_filename.replace("\"", "")
    input_filename = input_filename.replace("'", "")

    result_format = get_output_format()
    result_filename = os.path.join(get_output_path(input_filename), get_output_name(input_filename))
    # get linecount for progressbar
    line_count = get_linecount(input_filename)
    # set separator from options (deactivates automatic detection)
    csv_separator = args.s if args.s else csv_separator
    # set number of showed paths from options
    number_of_showed_paths = args.n if args.n else number_of_showed_paths
    # set list of datefields
    generate_datefields_list()

    # analyze file
    print(f"Analyzing file '{input_filename}'...")
    analyze_file(input_filename)
    if len(invalid_lines) > 0:
        print()
        print("  !!! Invalid rows detected in CSV and ignored in processing")
        print("  !!! Rows: ", end="")
        for l in invalid_lines:
            print(l, end="  ")
        print()
    print()

    # process data
    print("Processing records...")
    processed = process_file()
    calculate_device_totals()
    print()

    # write output-files
    print("Write result files...")
    name_for_thumbcache = config["other"]["name_for_thumbcache"]
    name_for_browsercache = config["other"]["name_for_browsercache"]
    if result_format == "txt":
        write_outputfile_txt()
    elif result_format == "json":
        write_outputfile_json()
    elif result_format == "docx":
        write_outputfile_docx()

    if config["result"]["generate_pathdetails"] and not args.nodetails:
        write_pathdetails()

    print()
    print()
    print(f"DONE! {processed} record processed (check results in '{result_filename}')")

except PathNotFoundException as exp:
    print()
    print("[!] Processing aborted!")
    print(">", exp.message)
except ColumnNotFoundException as exp:
    print()
    print("[!] Processing aborted!")
    print(">", exp.message)
except SeparatorNotFoundException as exp:
    print()
    print("[!] Processing aborted!")
    print(">", exp.message)
except FileNotFoundError as exp:
    print()
    print("[!] Processing aborted!")
    print(f"> File '{exp.filename}' not found")
except KeyError as exp:
    print()
    print("[!] Processing aborted!")
    print(f"> Configuration '{exp}' not found")
except UnicodeDecodeError as exp:
    print()
    print("[!] Processing aborted!")
    if exp.args[0] == "utf-8":
        print("File is not in UTF-8 format. Please adjust configuration or convert the file...")
    else:
        print("File is in an unknown format")
except UnicodeError as exp:
    print()
    print("[!] Processing aborted!")
    if "UTF-16" in exp.args[0]:
        print("File is not in UTF-16 format. Please adjust configuration or convert the file...")
    else:
        print("File is in an unknown format")
except Exception as exp:
    print()
    print("[!] Processing aborted!")
    traceback.print_exc()
