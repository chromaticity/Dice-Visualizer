from tkinter import *
import colorsys

# hsl(261, 100%, 50%) gradient color 1
# hsl(286, 100%, 50%) gradient color 2

colora = 261
colorb = 290


def interpolate(
    h1, h2, d
):  # first color, second color, how much of the way from hue1 to hue2 (0-1)
    if h1 > h2:
        return interpolate(h2, h1, d)
    return h1 + (h2 - h1) * d


def rgbtohex(r, g, b):
    if not (isinstance(r, int) and isinstance(g, int) and isinstance(b, int)):
        return rgbtohex(int(r), int(g), int(b))
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


# some settings
windowsize = 1350
# end of settings


win = Tk()
win.geometry(str(windowsize) + "x" + str(windowsize))
canvas = Canvas(win, width=windowsize, height=windowsize)
canvas.configure(bg="gray10")
canvas.pack()
win.resizable(width=0, height=0)
win.winfo_toplevel().title("Dice Visualizer")

currentdice = [6, 6]
customdice = [[1, 2, 4, 8]]


def namedice(dice):
    amounts = {}
    customamounts = [0] * len(customdice)
    for item in dice:
        if isinstance(item, int):
            if item in amounts:
                amounts[item] += 1
            else:
                amounts[item] = 1
        else:
            customamounts[int(item)] += 1

    keys = sorted(amounts.keys())
    name = ""
    for key in keys:
        amount = amounts[key]
        if amount == 1:
            name += "d" + str(key)
        else:
            name += str(amount) + "d" + str(key)
        if key != keys[-1]:
            name += ", "
    for i in range(len(customamounts)):
        if customamounts[i] != 0:
            if name != "":
                name += ", "
            if customamounts[i] == 1:
                name += "c" + str(i + 1)
            else:
                name += str(customamounts[i]) + "c" + str(i + 1)
    return name


def rollmin():
    minimum = 0
    for item in currentdice:
        if isinstance(item, int):
            minimum += 1
        else:
            minimum += min(customdice[int(item)])
    return minimum


def calculate(dice, probability):
    cases = [1]
    for d in dice:
        if isinstance(d, str):
            info = customdice[int(d)]
            maximum = max(info)

            cases += maximum * [0]
            for i in range(len(cases) - maximum - 1, -1, -1):
                for j in info:
                    cases[i + j] += cases[i]
                cases[i] = 0
        else:
            cases += d * [0]

            for i in range(len(cases) - d - 1, -1, -1):
                for j in range(1, d + 1):
                    cases[i + j] += cases[i]
                cases[i] = 0

    while cases[0] == 0:
        cases.pop(0)

    if probability:
        product = 1
        for item in dice:
            if isinstance(item, int):
                product *= item
            else:
                product *= len(customdice[int(item)])

        return [item / product for item in cases]
    else:
        return cases


def visualize():
    canvas.delete("all")
    probabilities = calculate(currentdice, True)

    greatest = max(probabilities)
    width = windowsize / len(probabilities)
    smalltextsize = round(width / 5)

    # graphs it
    for i in range(len(probabilities)):
        color = colorsys.hls_to_rgb(
            round(interpolate(colora, colorb, probabilities[i] / greatest)) / 360,
            0.5,
            1,
        )
        color = rgbtohex(color[0] * 255, color[1] * 255, color[2] * 255)
        y = windowsize - (probabilities[i] / greatest) * windowsize * 0.75
        canvas.create_rectangle(
            width * i,
            windowsize,
            width * (i + 1),
            y,
            fill=color,
            width=round(min(width / 20, 1)),
        )
        if smalltextsize > 2:
            canvas.create_text(
                width * (i + 0.5),
                y - smalltextsize * 2.5,
                text=str(round(probabilities[i] * 10000) / 100) + "%",
                fill="white",
                font=("Arial", smalltextsize),
            )
            canvas.create_text(
                width * (i + 0.5),
                y - smalltextsize,
                text=str(i + rollmin()),
                fill="white",
                font=("Arial", smalltextsize),
            )

    # dice info
    canvas.create_text(
        windowsize / 2,
        windowsize / 20,
        text=namedice(currentdice),
        fill="white",
        font=("Arial", round(windowsize / 30)),
    )

    # custom dice stuff
    for i in range(len(customdice)):
        canvas.create_text(
            windowsize * 0.025,
            windowsize * (0.04 + 0.025 * i),
            text="Custom Die " + str(i + 1) + " - " + str(customdice[i]),
            fill="white",
            font=("Arial", round(windowsize / 75)),
            anchor="w",
        )


def formatdigit(x):
    if isinstance(x, int):
        return ("d", 1, x)
    return x


def decode(text):
    if text.isdigit():
        if int(text) >= 1:
            return int(text)
    else:
        if "d" in text or "c" in text:
            letter = ""
            if "d" in text:
                data = text.split("d")
                letter = "d"
            else:
                data = text.split("c")
                letter = "c"

            if data[0] == "":
                data[0] = "1"
            data.insert(0, letter)
            if (data[1].isdigit() and int(data[1]) >= 1) and (
                data[2].isdigit() and int(data[2]) >= 1
            ):
                data[1] = int(data[1])
                data[2] = int(data[2])
                return data
        else:
            inputlist = text.split(",")
            for i in range(len(inputlist)):
                if inputlist[i][0] == " ":
                    inputlist[i][1:]
                if inputlist[i].isdigit() and (int(inputlist[i]) >= 1):
                    inputlist[i] = int(inputlist[i])
                else:
                    return -1
            return inputlist

    return -1


def buttonpress():
    i = retrieve_input()
    if i != -1 and (isinstance(i, int) or isinstance(i[0], str)):

        i = formatdigit(i)
        if i[0] == "c":
            i[2] -= 1
            if i[2] >= len(customdice):
                return
            for j in range(i[1]):
                currentdice.append(str(i[2]))
        else:

            for j in range(i[1]):
                currentdice.append(i[2])
        visualize()


def button2press():
    i = retrieve_input()

    if i != -1 and (isinstance(i, int) or isinstance(i[0], str)):
        i = formatdigit(i)
        if i[0] == "c":
            i[2] -= 1
            if i[2] >= len(customdice):
                return
            for j in range(i[1]):
                if str(i[2]) in currentdice:
                    currentdice.remove(str(i[2]))
        else:
            for j in range(i[1]):
                if i[2] in currentdice:
                    currentdice.remove(i[2])
        visualize()


def button3press():
    i = retrieve_input()
    if i != -1:
        if isinstance(i, int):
            if [i] not in customdice:
                customdice.append([i])
        else:
            if isinstance(i[0], int):
                sortedi = sorted(i)
                if sortedi not in customdice:
                    customdice.append(sortedi)

    visualize()


def button4press():
    i = retrieve_input()
    if i != -1 and (not isinstance(i, list)) and i <= len(customdice):
        if isinstance(i, str):
            i = int(i)
        customdice.pop(i - 1)
        j = 0
        while j < len(currentdice):
            if currentdice[j] == str(i - 1):
                currentdice.pop(j)
                j -= 1
            j += 1
        for k in range(len(currentdice)):
            if isinstance(currentdice[k], str) and int(currentdice[k]) > i - 1:
                currentdice[k] = str(int(currentdice[k]) - 1)
        visualize()


def retrieve_input():
    return decode(textbox.get("1.0", "end-1c"))


textbox = Text(
    win, relief="flat", fg="white", bg="gray20", font=("Arial", round(windowsize / 40))
)
textbox.place(
    x=round(windowsize * 0.7875),
    y=round(windowsize * 0.075),
    width=windowsize / 5,
    height=windowsize / 20,
)

button = Button(win, text="Add", command=lambda: buttonpress())
button.place(
    x=round(windowsize * 0.7875),
    y=round(windowsize * 0.01),
    width=windowsize * 0.09,
    height=windowsize / 20,
)

button2 = Button(win, text="Remove", command=lambda: button2press())
button2.place(
    x=round(windowsize * 0.8975),
    y=round(windowsize * 0.01),
    width=windowsize * 0.09,
    height=windowsize / 20,
)

button3 = Button(win, text="Define", command=lambda: button3press())
button3.place(
    x=round(windowsize * 0.7875),
    y=round(windowsize * 0.14),
    width=windowsize * 0.09,
    height=windowsize / 20,
)

button4 = Button(win, text="Undefine", command=lambda: button4press())
button4.place(
    x=round(windowsize * 0.8975),
    y=round(windowsize * 0.14),
    width=windowsize * 0.09,
    height=windowsize / 20,
)

visualize()

win.mainloop()

