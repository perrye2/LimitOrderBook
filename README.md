# RGM Advisors Order Book Programming Problem

## Overview

This project uses Python to solve the RGM Advisors [Order Book Programming Problem](http://rgmadvisors.com/problems/orderbook/ "Order Book Programming Problem") posted on the [careers](http://rgmadvisors.com/careers.html) section of their [website](http://rgmadvisors.com/). I have not applied for a position with RGM Advisors, but I found this programming challenge interesting and decided to complete it.

The task first involves assembling a "limit order book" from a series of market data messages. The messages either *add* an order to the book or *reduce* the size of an existing order (sometimes eliminating it entirely). The order book is naturally separated into two sides, one representing outstanding limit orders to *buy* (called "bids") and the other representing outstanding limit orders to *sell* (called "asks"). In this project, each side of the order book is represented using an instance of the `OrderBook` class. Each `OrderBook` object makes use of two main data structures, `price_map` and `order_map`.

`price_map` is a Python dictionary (hash map) that maps a *price* to the **total** *size* at 
that *price* on that side of the book.

`order_map` is a Python dictionary (hash map) that maps an *order-id* to a *price* and *size*.

As each market data message is processed and the order book is modified accordingly, the program calculates the total expense incurred if *target-size* shares were bought (by taking as many asks as necessary, lowest first) and the total income received if *target-size* shares were sold (by hitting as many bids as necessary, highest first). Every time there is a change to the expense or income, the program outputs the new value.

For reference, a copy of the original problem statement, exactly as it appeared on RGM Advisors' website at the time of this writing, is included in this repository in `OriginalProblemStatement.pdf`.


## Usage

The `pricer.py` program was developed using **Python 2.7** and is not guaranteed to run with other versions of Python. The user **must** specify a *target-size* representing the number of shares to be bought or sold. An input file can either be specified as a command-line argument or read from standard input. All output is directed to standard output. Examples of how to run the program are shown below:

First, with *target-size* = 200 and passing the input via standard input:

```> python pricer.py 200 < pricer.in```

Or, alternatively, passing an input file name as a command-line argument:

```> python pricer.py 200 pricer.in```

The input file, `pricer.in`, as well as three reference output files for *target-size* = 1, 200, and 10,000 are included in this repository. These files are relatively large, so they've been compressed.


## Answers to Questions

In addition to supplying the source code to solve the problem outlined above, they ask for answers to the following
questions:

* **How did you choose your implementation language?**

   I chose Python because I enjoy using it to solve problems. It's excellent for rapid prototyping tasks, such as coding challenges, and it's also well-suited for larger software projects. It's easy to use, has a fairly extensive standard library, and has a large community of users.
* **What is the time complexity for processing an *Add Order* message?**
    
   Because orders are stored in Python dictionaries (hash maps), processing an 
*Add Order* message is O(1).
* **What is the time complexity for processing a *Reduce Order* message?**  
 
   Again, because orders are stored in Python dictionaries (hash maps), processing
 a *Reduce Order* message is O(1).
* **If your implementation were put into production and found to be too slow, 
what ideas would you try out to improve its performance? 
(Other than reimplementing it in a different language such as C or C++.)**

   Ignoring minor performance tweaks and the obvious improvements we'd realize by using a compiled language, like C or C++, rather than an interpreted one, like Python, the two main bottlenecks in this implementation are file I/O and the fact that the price levels in the order book need to be sorted each time a change in expense or income is calculated. These issues are discussed below.

   As stated, the problem requires inputs be read as text from standard input, and outputs be sent as text to standard output, so our options are limited for improving file I/O latency. However, in production, we may have the flexibility to do file I/O using a binary format, which could potentially be much faster than the current text format.
   
   Because the price levels on both sides of the order book are stored in unsorted data structures, each time the code calculates the expense or income associated with buying or selling the *target-size* number of shares, it needs to sort the price levels. Specifically, the program needs to sort the dictionary keys, which represent the prices on a given side of the book, each time it calculates the change in expense or income. This sort operation has a time complexity of O(n log n). This could potentially be improved by using a data structure that keeps the keys sorted automatically, such as a red-black tree. However, that type of implementation presents a trade-off: while we would no longer need to sort the keys each time and could instead access the elements in O(log n) time, the time complexity of an *Add Order* and *Reduce Order* increases to O(log n) from O(1). There are some limit order book implementations that are able to reduce the time complexity of these operations through the use of additional data structures while storing price levels in a binary search tree, but for this exercise, the problem statement stipulates that the solution use only the chosen language's standard library, and as of this writing, Python's standard library does not include binary search trees. Implementing this type of data structure was beyond the scope of this problem.