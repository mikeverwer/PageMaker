'''
Written by Mike Verwer, M.Sc. Mathematics
'''
def row_print(to_print, items_per_line=10, string=False) -> str | None:
    """
    Prints a single list in rows

    Parameters:
        :param to_print: A list of things to print
        :param items_per_line: The number of items to prints per line; A.K.A., number of rows. default = 10
        :param string: Determines if the function returns a string or prints on its own.
    """

    max_width = max(len(str(item)) for item in to_print)

    if string:
        printable = ''
        # Loop through the list and print (default) 10 items per line
        for i, item in enumerate(to_print, 1):
            printable += f"{str(item):<{max_width}} "

            if i % items_per_line == 0:  # Check if we've reached the desired items per line
                printable += '\n'  # Move to the next line

        return printable

    else:
        # Loop through the list and print (default) 10 items per line
        for i, item in enumerate(to_print, 1):
            print(f"{str(item):<{max_width}}", end=' ')

            if i % items_per_line == 0:  # Check if we've reached the desired items per line
                print()  # Move to the next line


def draw_bars(hbars, hbar, vbars, vbar, row_length, heading_space, column_width, cutoff, string):
    printable = ''
    if bool(hbars) and not bool(vbars):
        if string:
            printable += hbar * (row_length - 1)
        else:
            print(hbar * (row_length - 1))

    if bool(vbars) and not bool(hbars):
        if vbars == 'full':
            if string:
                printable += ' ' * heading_space + vbar
            else:
                print(' ' * heading_space + vbar, end='')
            for _ in range(1, cutoff + 1):
                if string:
                    printable += ' ' * (column_width + 1) + vbar
                else:
                    print(' ' * (column_width + 1) + vbar, end='')
            if string:
                printable += '\n'
            else:
                print()
        else:
            if string:
                printable += ' ' * heading_space + vbar
            else:
                print(' ' * heading_space + vbar)

    if bool(hbars) and bool(vbars):
        row_length += len(vbar) * cutoff if vbars == 'full' else row_length
        if string:
            printable += hbar * heading_space + vbar + hbar * (row_length - heading_space - len(vbar) - 1) + vbar
        else:
            print(hbar * heading_space + vbar + hbar * (row_length - heading_space - len(vbar) - 1) + vbar)

    if not bool(hbars) and not bool(vbars):
        if string:
            printable += '\n'
        else:
            print('\n')

    if string:
        return printable


def multi_list_print(lists: list[list[any]], headings: list[str] = None, cutoff: int = 10, give_string: bool = False,
                     hbars: bool | str = True, vbars: bool | str = 'full',
                     headings_every_row: bool = True,
                     universal_column: bool = True, universal_width: int = None,
                     recursion: bool = False, heading_space: int = None, string: str = ''
                    ) -> str | None:
    """
    Prints multiple lists in rows via recursion.  If any of the lists are larger than :param cutoff:, a multi-linebreak occurs and
    the remaining entries continue printing. If :param hbars: is True the multi-linebreak is drawn as a horizontal bar.
    Headings can also be added to be printed before the lists, with the option of having them displayed with each multi-
    linebreak.  If :param_vbars: is True, vertical bars are drawn to separate the headings from the lists.

    :param lists: Type - list of lists: The lists for printing. Must be a list of lists. Must be present.
    :param headings: type - list of strings: A list of strings to be used as headings.
        currently: If present, # of headings must be equal to # of lists, or only first len(headings) lists get printed.
    :param cutoff: Type - int: Number of elements to print per multi-line
    :param hbars: Type - bool: Controls if horizontal bars are drawn at multi-linebreaks
    :param vbars: Type - bool or string: Controls if vertical bars are drawn to separate headings from the list entries
        If set to True: Draws one vertical bar separating the headings from the lists
        If set to 'full' - Draws vertical bars separating all columns
    :param headings_every_row: Type - bool: Controls if headings are displayed on every multi-line or only the first.
        If set to False, headings are only included in the first multi-line but each one after will be justified by the
        max heading length to ensure the columns align.
    :param universal_column: Type - bool: Controls if all rows of all multi-lines are printed with a fixed, universal
        column width. If set to False, the rows of each multi-line will be printed with a column width determined by the
        longest entry in the multi-line.
    :param universal_width:  Type - int: Sets the column width if universal_column is True.
        If None, automatically gets set to the length of the largest item of all the lists.
        Recommended to keep set to None.
    :param recursion: Type - bool: For internal use only: DO NOT SET TO TRUE. Indicates if the pass is recursive.
    :param heading_space: Type - int: For internal use only: required for recursion pass.
    :param string: Type - str: Recursively pass the string being built
    :return: printable if give_string is True
    """
    printable = string
    leftovers = None
    skip_vbars = False
    number_of_lists = len(lists)
    has_headings = False if headings is None or headings == [' '] * number_of_lists else True
    hbar = '\u2500' if bool(hbars) else ''
    vbar = '\u2502' if bool(vbars) else ''
    if recursion or not bool(vbars):
        skip_vbars = True

    #  getting list info
    if not recursion:  # user pass - aka: first pass
        heading_space = []
        if has_headings:
            for heading in headings:  # appending space to headings if needed
                heading += ' ' if heading[-1] != ' ' else heading
                heading_space.append(len(heading))
            heading_space = max(heading_space)
        else:
            headings = [''] * number_of_lists
            heading_space = 0

        universal_width = max(  # sets width to the length of the longest item over all lists, if needed
                max(len(str(item)) for item in sublist) if sublist else 0
                for sublist in lists
            ) if (universal_width is None or universal_width == 0) else 0

    max_list_length = max(len(original_list) for original_list in lists)
    temp_lists = [original_list.copy() for original_list in lists]

    # check list lengths against cutoff. grab the first 'cutoff' entries for printing, remember the leftovers.
    if max_list_length >= cutoff:
        short_lists = [temp_list[:cutoff] for temp_list in temp_lists]
        leftovers = [temp_list[cutoff:] for temp_list in temp_lists]
        temp_lists = [short_list for short_list in short_lists]

    # justifying and adding headers as the 0th entry of each list. adding vbars if requested
    if has_headings or bool(vbars):
        headings = [heading + ' ' * (heading_space - len(heading)) + vbar if not skip_vbars
                    else heading.ljust(heading_space) for heading in headings]
        temp_lists = [[heading] + temp_list for heading, temp_list in zip(headings, temp_lists)]

    # set the column width for this multiline to the longest entry in multi-line, or the universal width
    column_width = universal_width if universal_column else max(  
            max(len(str(item)) for item in sublist) if sublist else 0
            for sublist in lists
        )

    row_length = (universal_width + 1) * cutoff + heading_space + len(hbar) if bool(hbars) else (len(vbar) if  bool(vbars) else 0)

    
    if not recursion:  # draw top bars
        if give_string:
            printable = ''
            printable += draw_bars(hbars, hbar, vbars, vbar, row_length, heading_space, column_width, cutoff, string=True) + '\n'
        else:
            draw_bars(hbars, hbar, vbars, vbar, row_length, heading_space, column_width, cutoff, string=False)

    # printing lists
    for temp_list in temp_lists:
        for index, item in enumerate(temp_list, 0):
            if index == 0:  # handle headings
                if has_headings:
                    if not headings_every_row and bool(vbars) and recursion:  # recursive pass, add header and vbar?
                        if give_string:
                            printable += f"{vbar:>{heading_space + 1}}" + ' '
                        else:
                            print(f"{vbar:>{heading_space + 1}}", end=' ')
                    else:
                        if give_string:
                            printable += f"{str(item):<{heading_space + 1}}" + ' '
                        else:
                            print(f"{str(item):<{heading_space + 1}}", end=' ')
                else:  # no heading
                    if give_string:
                        printable += vbar + ' '
                    else:
                        print(vbar + ' ')
            else:  # regular list item
                if give_string:
                    printable += f"{str(item) :<{column_width}}" + (vbar if vbars == 'full' else '') + ' '
                else:
                    print(f"{str(item) :<{column_width}}" + (vbar if vbars == 'full' else ''), end=' ')
        if give_string:
            printable += '\n'
        else:
            print()  # Move to the next line

    if give_string:
        printable += draw_bars(hbars, hbar, vbars, vbar, row_length, heading_space, column_width, cutoff, string=give_string)
    else:
        draw_bars(hbars, hbar, vbars, vbar, row_length, heading_space, column_width, cutoff, string=give_string)

    if give_string:
        printable += '\n'

    if max_list_length - cutoff > 0:
        return multi_list_print(leftovers, [heading for heading in headings] if headings_every_row
        else [' ' * heading_space for _ in headings], cutoff, give_string, hbars, vbars, headings_every_row,
                         universal_column, universal_width, string=printable if printable is not None else '', recursion=True, heading_space=heading_space)
    else:
        if give_string and printable is not None:
            return printable


def main():
    # Full usable argument list:
    # multi_list_print(
    #    lists= [['aaaaaaaaaaaaaaa'] + [str(x) for x in range(1, 102)], [str(int(i) ** 2) for i in range(1, 102)],
    #      [str(int(i) ** 3) for i in range(1, 102)], [str(int(i) ** 4) for i in range(1, 102)]],
    #    headings=['x', 'x^2', 'x^3', 'x^4'], 
    #    cutoff=10,
    #    hbars=True, 
    #    vbars='full', 
    #    headings_every_row=True, 
    #    universal_column=True, 
    #    string=False
    # )

    # column_print([str(x ** 2) for x in range(1, 101)], items_per_line=25)

    multi_list_print([[str(i) for i in range(1, 101)], [str(i ** 4) for i in range(1, 101)]], ['x', 'x^4'])
    print('The above was printed with many calls to print(), using multi_list_print(lists, headings, give_string=False).')


    print(multi_list_print(lists=[[str(i) for i in range(1, 101)], [str(i ** 4) for i in range(1, 101)]], headings=['x', 'x^4'], give_string=True))
    print('The above was printed with 1 call to print(), using multi_list_print(lists, headings, give_string=True).')

if __name__ == '__main__':
    main()
