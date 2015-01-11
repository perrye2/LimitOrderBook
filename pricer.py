"""This code solves the RGM Advisors Order Book Programming Problem.
See github.com/perrye2/LimitOrderBook for more information.
"""
import sys
import time
try:
    import argparse
except ImportError:
    error_string = ("ERROR: Can't import argparse. The argparse module "
                    "is packaged with Python 2.7 and later.\n")
    sys.stderr.write(error_string)


class Order(object):
    """A simple class to represent an add or reduce order."""
    def __init__(self):
        self.timestamp = int()
        self.type = str()
        self.id = str()
        self.size = int()
        self.price = int()
        self.side = str()

    def parse_message(self, raw_line):
        """Parse a raw input line string into an Order object."""
        raw_line.strip()
        message = raw_line.split(" ")
        self.timestamp = int(message[0])
        self.type = message[1]
        self.id = message[2]
        if len(message) == 4:
            # reduce order
            self.size = int(message[3])
            self.price = None
            self.side = None
        else:
            # add order
            self.size = int(message[5])
            # represent the price as an integer number of cents.
            # care is taken to account for possible imprecise
            # representation of price as a float after conversion
            # from string.
            self.price = int(float(message[4])*100.0 + 0.5)
            self.side = message[3]

    def __str__(self):
        """Simple method to display an Order object."""
        if self.price is not None:
            # print add order
            # convert the integer number of cents back to a
            # floating point representation of dollars and cents.
            return ("Order -> Timestamp: %d, Type: %s, ID: %s, Side: %s, "
                    "Price: %.2f, Size: %d" %
                    (self.timestamp, self.type, self.id, self.side,
                     float(self.price)/100.0, self.size))
        else:
            # print reduce order
            return ("Order -> Timestamp: %d, Type: %s, ID: %s, Size: %d" % 
                    (self.timestamp, self.type, self.id, self.size))


class OrderBook(object):
    """A class representing one side of an order book.
    The key data structures are price_map and order_map.

    price_map is a dictionary that maps a price to the total
    size at that price on this side of the book.

    order_map is a dictionary that maps an order_id to a dictionary
    containing two elements, price and size.
    """
    def __init__(self, side_string):
        # side of the book, buy or sell, "B" or "S"
        self.side = side_string
        # represents open interest on this side of the book
        self.total_size = 0
        # maps price to total size at that price on this side of the book
        self.price_map = {}
        # maps order_id to a dict containing two elements, price and size
        self.order_map = {}

    def process_order(self, order):
        """Depending on the order type, pass the order to the
        appropriate method to handle it. Takes an Order object
        as an argument.
        """
        if order.type == "A":
            self._add_order(order)
        elif order.type == "R":
            self._reduce_order(order)

    def _add_order(self, order):
        """Add a new order to this side of the book. Takes an
        Order object as an argument.
        """
        if self.side == order.side:
            self.order_map[order.id] = {'price' : order.price,
                                        'size' : order.size}
            if order.price in self.price_map:
                self.price_map[order.price] += order.size
            else:
                self.price_map[order.price] = order.size
            self.total_size += order.size
        else:
            return

    def _reduce_order(self, order):
        """Reduce an existing order if it's currently on this
        side of the book. Takes an Order object as an argument.
        """
        if self.order_id_exists(order):
            reduce_size = order.size
            price = self.order_map[order.id]['price']
            # reduce first
            self.order_map[order.id]['size'] -= reduce_size
            self.price_map[price] -= reduce_size
            self.total_size -= reduce_size
            # remove if necessary
            if self.order_map[order.id]['size'] == 0:
                del self.order_map[order.id]
            if self.price_map[price] == 0:
                del self.price_map[price]
        else:
            return

    def order_id_exists(self, order):
        """Check if an order_id currently exists on this side
        of the book. Takes an Order object as an argument.
        """
        if order.id in self.order_map:
            return True
        else:
            return False

    def calc_cost(self, target):
        """If this side of the book contains enough size to process
        an order of size target, calculate the cost of processing
        that order. This is slightly different depending on if we're
        calculating the cost associated with buying or selling. Takes
        target size as an argument.
        """
        if self.total_size >= target:
            remaining = target
            cost = 0
            prices = self.price_map.keys()
            # for buying, we sort in descending order, for selling, we sort in
            # ascending order. these sorts are costly in terms of execution
            # time - this is where we could potentially benefit from a sorted
            # dictionary.
            if self.side == "B":
                prices.sort(reverse = True)
            elif self.side == "S":
                prices.sort()
            # loop through all prices until we've transacted the target amount.
            level_count = 0
            while remaining > 0:
                this_price = prices[level_count]
                this_size = self.price_map[this_price]
                if remaining >= this_size:
                    cost += this_price*this_size
                    remaining -= this_size
                else:
                    cost += this_price*remaining
                    remaining = 0
                level_count += 1
        else:
            cost = 0
        return cost

    def __str__(self):
        """Simple method to display an OrderBook object."""
        str_list = []
        prices = self.price_map.keys()
        if self.side == "B":
            str_list.append("********* BIDS *********\n")
            prices.sort(reverse=True)
        elif self.side == "S":
            str_list.append("********* ASKS *********\n")
            prices.sort()
        for price in prices:
            # convert the integer number of cents back to a
            # floating point representation of dollars and cents.
            string = ("Price: %.2f, Size: %d\n" %
                    (float(price)/100.0, self.price_map[price]))
            str_list.append(string)
        return "".join(str_list)


def print_output(order, side_string, new_amnt, old_amnt):
    """If there is a change in the amount that can be bought or sold,
    print out the new amount. Special handling for the case when the
    new amount is 0.
    """
    if new_amnt != old_amnt:
        if new_amnt != 0:
            # convert the integer number of cents back to a
            # floating point representation of dollars and cents.
            print ("%d %s %.2f" % (order.timestamp, side_string,
                                   float(new_amnt)/100.0))
        else:
            print "%d %s NA" % (order.timestamp, side_string)
    else:
        return


if __name__ == "__main__":
    # this allows us to make use of some code that was handy 
    # development and debugging
    debug_flag = False
    if debug_flag:
        # keep this around for debugging and testing
        args = {}
        args["target_size"] = 200
        filename = "pricer.in"
        args["in_file"] = open(filename, "r")
        target_size = args["target_size"]
        # timing during development
        start_time = time.time()
    else:
        # specialized argument parsing, requires Python 2.7 or later
        parser = (argparse.ArgumentParser(description="Pricer tool for RGM "
                "Advisors Order Book Programming Problem. Requires user to "
                "specify a target size as a command-line argument. An input "
                "file can either be specified as a command-line argument or "
                "read from standard input. All output is directed to standard "
                "output."))
        parser.add_argument("target_size", type=int, help="Target size")
        parser.add_argument("in_file", nargs="?", type=argparse.FileType("r"),
                            default=sys.stdin, help="Input file")
        # process arguments
        args = vars(parser.parse_args())
        target_size = args["target_size"]

    # initialize Order and OrderBook objects.
    single_order = Order()
    buy_ob = OrderBook("B")
    sell_ob = OrderBook("S")

    # we'll use these to keep track of size changes on either side
    # of the book. by caching the total outstanding buy and sell
    # amounts, we only need to calculate the cost of buying and
    # selling if these amounts change, which improves efficiency.
    cached_total_bid_size = 0
    cached_total_ask_size = 0

    # initialize the buy and sell amounts. we report a change in
    # buying and selling amounts only if these change when a new
    # order is processed by the order book.
    cached_buy_amnt = 0
    cached_sell_amnt = 0

    # loop through all messsages
    for line in args["in_file"]:
        # read the line into an Order object
        try:
            single_order.parse_message(line)
        except ValueError:
            # account for errors in the input file, keep going if
            # possible. this could obviously be much more robust and
            # could include error checking in the Order class.
            error_string = ("WARNING: Error detected in input file. "
                            "Attempting to continue...\n")
            sys.stderr.write(error_string)
        # process order
        buy_ob.process_order(single_order)
        sell_ob.process_order(single_order)
        # try buying and selling only if the size on either side of
        # the book has changed
        if sell_ob.total_size != cached_total_ask_size:
            cached_total_ask_size = sell_ob.total_size
            new_buy_amnt = sell_ob.calc_cost(target_size)
            print_output(single_order, "B", new_buy_amnt, cached_buy_amnt)
            cached_buy_amnt = new_buy_amnt
        if buy_ob.total_size != cached_total_bid_size:
            cached_total_bid_size = buy_ob.total_size
            new_sell_amnt = buy_ob.calc_cost(target_size)
            print_output(single_order, "S", new_sell_amnt, cached_sell_amnt)
            cached_sell_amnt = new_sell_amnt

    # not necessary for standard input, but keep around for when an
    # input file is passed in as a command-line argument. this could
    # be wrapped in try/except.
    args["in_file"].close()

    if debug_flag:
        # timing during development
        print time.time() - start_time, "seconds elapsed"
        