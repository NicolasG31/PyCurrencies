"""
Imports the Python libraries needed to the project.
Some are necessary to calculate decimal values, others to download a file via an URL.
"""
import sys
import zipfile
from collections import defaultdict
from decimal import Decimal
from urllib.request import urlretrieve

"""
Imports the libraries needed for PyQt.
These are necessary to display the Qt interface and the graph.
"""
import pyqtgraph as pg
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import *

"""
Main class based on QDialog.
The program starts from here.
"""
class Form(QDialog):
    """
    __init__ method which sets what happens when we initialize our main class.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        """
        Here we initialize our data.
        
        self.content -> Contains all the data we extracted from the file we downloaded
        via the method self.download_unzip().
        
        self.currencies -> An array we just initialize. It will later contain our currencies codes.
        
        self.data -> A dictionary we just initialize. Will contain our dictionaries with the 
        currencies values associated to dates.
        
        self.get_data -> Fills the data and currencies variables.
        """
        self.content = self.download_unzip()  # returns the content of the file downloaded
        self.currencies = []
        self.data = defaultdict(dict)  # initialize a default dictionary
        self.get_data()

        """
        These two variables initialize two dates by default when the program starts.
        Allows to display a default graph with 7 days difference from the most recent date found in the file. 
        """
        self.date1 = QDate.fromString(self.recent_date, 'yyyy-MM-dd').addDays(-7)
        self.date2 = QDate.fromString(self.recent_date, 'yyyy-MM-dd')

        """
        Two arrays which will contain the rates to display on the graph.
        They will be filled later when we update the graph.
        """
        self.rates1 = []
        self.rates2 = []

        """
        Label to display the latest date found in the file.
        """
        self.recentDateLabel = QLabel()
        self.recentDateLabel.setText("Most recent date: " + self.recent_date)

        """
        ComboBox which will display and allow the user to select the original currency.
        We connect it to the list of currencies we previously filled.
        """
        self.from_currency = QComboBox()
        self.from_currency.addItems(self.currencies)

        """
        SpinBox which will allow the user to enter the amount to be converted.
        We set a minimum value to 0.01 and a maximum value to 10000000.00.
        The default value is 1.00.
        """
        self.from_amount = QDoubleSpinBox()
        self.from_amount.setRange(0.01, 10000000.00)
        self.from_amount.setValue(1.00)

        """
        ComboBox which will display and allow the user to select the destination currency.
        We connect it to the list of currencies we previously filled.    
        """
        self.to_currency = QComboBox()
        self.to_currency.addItems(self.currencies)

        """
        Label to display the result of the conversion.
        The default string is set to display 1.00, as the default result will be 1.00.
        """
        self.to_amount = QLabel("Result of conversion based on most recent rates: 1.00")

        """
        Initialize the grid layout.
        We then add one by one the different widgets we've previously created to a certain place in the grid.
        The grid layout is then set to be the layout of our application.
        """
        self.grid = QGridLayout()
        self.grid.addWidget(self.recentDateLabel, 0, 0)
        self.grid.addWidget(self.from_currency, 1, 0)
        self.grid.addWidget(self.from_amount, 1, 1)
        self.grid.addWidget(self.to_currency, 2, 0)
        self.grid.addWidget(self.to_amount, 2, 1)
        self.setLayout(self.grid)

        """
        Initialize the two values with the default text from the ComboBoxes which contain
        the currencies.
        """
        self.to_ = self.to_currency.currentText()
        self.from_ = self.from_currency.currentText()

        """
        Methods to display the calendars and the graph.
        """
        self.display_calendars()
        self.display_graph()

        """
        When we change a currency ComboBox or the value to convert, we call the function
        update_ui() which will obviously update the UI.
        """
        self.from_currency.currentIndexChanged.connect(self.update_ui)
        self.to_currency.currentIndexChanged.connect(self.update_ui)
        self.from_amount.valueChanged.connect(self.update_ui)

        """
        Sets the name of the program window. 
        """
        self.setWindowTitle("Currency converter")

    """
    Recalculates and updates the UI.
    """
    def update_ui(self):
        try:
            """
            Gets the currencies codes from the ComboBoxes.
            """
            self.to_ = self.to_currency.currentText()
            self.from_ = self.from_currency.currentText()

            """
            Gets the currencies most recent values in the dictionary 'data'.
            """
            to_amt = Decimal(self.data[self.to_][self.recent_date])
            from_amt = Decimal(self.data[self.from_][self.recent_date])

            """
            If there is an unknown value coming from the data dictionary (set to 0),
            we set the Label to inform the user that there is a missing information.
            """
            if to_amt == 0 or from_amt == 0:
                self.to_amount.setText("Unknown due to missing data")
            else:
                """
                If the currencies values aren't missing, we get the value the user has entered in the SpinBox
                and then convert it.
                The result is then displayed on the Label.
                """
                amt = Decimal(self.from_amount.value())
                amount = (to_amt / from_amt) * amt
                self.to_amount.setText("Result of conversion based on most recent rates: %.02f" % amount)

            """
            We update the graph.
            """
            self.update_graph()
        except Exception as e:
            """
            If there is an error during the conversion, we print it in the console
            and set the Label to say something went wrong. 
            """
            print("Error while converting: ", e)
            self.to_amount.setText("Error while converting")

    """
    Method that will download and unzip the file containing the data we need.
    Returns its content.
    """
    def download_unzip(self):
        try:
            """
            Retrieves the url file and extracts its first file.
            We then open that file and return its content as lines.
            """
            url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip'
            file, _ = urlretrieve(url)
            zip_file_object = zipfile.ZipFile(file, 'r')
            first_file = zip_file_object.namelist()[0]
            file = zip_file_object.open(first_file)
            return file.readlines()
        except Exception as e:
            print(e)
            return "Failed to download or unzip"
        finally:
            file.close()

    """
    Method that will retrieve the data from the content of the file we've previously opened.
    """
    def get_data(self):
        try:
            """
            Initialize an array, and puts in the decoded data from each line of the file.
            """
            lines = []
            for line in self.content:
                lines.append(line.decode())

            """
            Retrieves the currencies code from the first line of the file and puts it
            in the 'currencies' array.
            """
            for cur in lines[0].split(",")[1:-1]:
                self.currencies.append(cur)

            """
            Goes through each line of the file to fill our data dictionary, which contains
            all the values from the dates available for each currencies.
            It basically creates a double dictionary : data[currency code][date][value] 
            """
            for line in lines[1:]:
                i = 1
                for cur in lines[0].split(",")[1:]:
                    split_line = line.split(",")
                    """
                    If the data from the file is unavailable ('N/A' here), we set the value
                    to 0.
                    """
                    if split_line[i] == "N/A":
                        self.data[cur][split_line[0]] = 0
                    else:
                        self.data[cur][split_line[0]] = split_line[i]
                    i += 1

            """
            Sets the most recent date from the file (which is the first line).
            """
            self.recent_date = lines[1].split(",")[0]
            """
            Sorts alphabetically the currencies codes.
            """
            self.currencies.sort()

        except Exception as e:
            print(e)
            return "Failed to extract data"

    """
    Methods which initializes the calendars and displays them.
    """
    def display_calendars(self):
        """
        Creates one calendar that we call 'Cal1'.
        We set the grid visible to true for more visibility.
        The date range is set from the file (the latest one being 1999/01/04 while
        the most recent is set in date2).
        A default date 'date1' is selected.
        """
        self.from_date = QCalendarWidget(self)
        self.from_date.setObjectName("Cal1")
        self.from_date.setGridVisible(True)
        self.from_date.setDateRange(QDate(1999, 1, 4), self.date2)
        self.from_date.setSelectedDate(self.date1)

        """
        Same as previous calendar, except the name is 'Cal2' and the
        default date 'date2' is selected.
        """
        self.to_date = QCalendarWidget(self)
        self.to_date.setObjectName("Cal2")
        self.to_date.setGridVisible(True)
        self.to_date.setDateRange(QDate(1999, 1, 4), self.date2)
        self.to_date.setSelectedDate(self.date2)

        """
        Connects the click event of the two calendars to the 'update_dates()' method.
        """
        self.from_date.clicked[QDate].connect(self.update_dates)
        self.to_date.clicked[QDate].connect(self.update_dates)

        """
        Adds the two calendars to the grid used in the layout.
        """
        self.grid.addWidget(self.from_date, 3, 0)
        self.grid.addWidget(self.to_date, 3, 1)

    """
    Method that updates the dates values when we click on a date from the calendar.
    """
    def update_dates(self, date):
        """
        Gets the event sender so we can identify who called it.
        We then update the variables date1 and date2 depending on which calendar was clicked.
        """
        sender = self.sender()
        if sender.objectName() == "Cal1":
            self.date1 = self.from_date.selectedDate()
        elif sender.objectName() == "Cal2":
            self.date2 = self.to_date.selectedDate()

        """
        Updates the graph as we've changed the dates.
        """
        self.update_graph()

    """
    Method which initialize and displays the graph.
    """
    def display_graph(self):
        """
        Creates a plot widget.
        We add this plot to the grid layout, telling it to use 2 length slots.
        We set the plot grid visible.
        Finally we add the legend and call to update the graph.
        """
        self.rates_plot = pg.PlotWidget()
        self.grid.addWidget(self.rates_plot, 4, 0, 1, 2)
        self.rates_plot.showGrid(x=True, y=True)
        self.legend = self.rates_plot.addLegend()
        self.rates_plot.setLabel('left', 'Rate')
        self.rates_plot.setLabel('bottom', 'Days')

        self.update_graph()

    """
    Methods which updates the graph.
    """
    def update_graph(self):
        """
        Clears the graph and the legend so we can write on it without duplicating.
        We then add again the legend -> solves the bug which makes the legend to duplicate.
        """
        self.rates_plot.clear()
        self.legend.scene().removeItem(self.legend)
        self.legend = self.rates_plot.addLegend()

        """
        Initializes our two arrays in which the currencies rates will be put.
        """
        self.rates1 = []
        self.rates2 = []

        """
        Calculates how many days there are between our selected dates.
        """
        diff = QDate.daysTo(self.date1, self.date2)

        """
        If the difference between these two dates is positive, which means date1 is before date2,
        we start filling our arrays.
        """
        if diff > 0:
            """
            Initalizing variables needed to fill the rates.
            """
            i = 0
            default1 = 0
            default2 = 0

            """
            For every day before date2, we verify if the date is available. If not, we get
            the last value found (or 0, if the first date we're looking for is missing).
            Else, we retrieve that value from our data dictionary and add it in the rates array.
            
            It is done for our 2 selected currencies.
            Each turn we increment the counter 'i' to get closer to 'date2' from 'date1'.
            """
            while i < diff:
                if self.date1.addDays(i).toString('yyyy-MM-dd') in self.data[self.to_]:
                    self.rates1.append(float(self.data[self.to_][self.date1.addDays(i).toString('yyyy-MM-dd')]))
                    default1 = float(self.data[self.to_][self.date1.addDays(i).toString('yyyy-MM-dd')])
                else:
                    self.rates1.append(default1)

                if self.date1.addDays(i).toString('yyyy-MM-dd') in self.data[self.from_]:
                    self.rates2.append(float(self.data[self.from_][self.date1.addDays(i).toString('yyyy-MM-dd')]))
                    default2 = float(self.data[self.from_][self.date1.addDays(i).toString('yyyy-MM-dd')])
                else:
                    self.rates2.append(default2)
                i += 1

            """
            Our third array is full of '1' because the conversion value stays the same as it serves
            as reference to convert.
            """
            conversion3 = [1] * diff

            """
            We set the graph axis ranges considering our data. 
            """
            date_range = range(0, diff)  # should be equal to the number of days you want to have in your x-axis
            self.rates_plot.setXRange(0, diff - 1)  # should be as wide as the number of dates we want to show
            self.rates_plot.setYRange(0, max(self.rates1 + self.rates2))  # should be as high as the max exchange

            try:
                x = range(0, diff)
                """
                Defines our 3 curves to display on the graph.
                """
                c1 = self.rates_plot.plot(date_range, self.rates1, pen='b', symbol='x', symbolPen='b',
                                          symbolBrush=0.2, name=self.to_currency.currentText())
                c2 = self.rates_plot.plot(date_range, self.rates2, pen='r', symbol='o', symbolPen='r',
                                          symbolBrush=0.2, name=self.from_currency.currentText())
                c1 = self.rates_plot.plot(date_range, conversion3, pen='g', symbol='+', symbolPen='g',
                                          symbolBrush=0.2, name='conversion rate')
            except Exception as e:
                print(e)


app = QApplication(sys.argv)
form = Form()
form.show()
sys.exit(app.exec_())