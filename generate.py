import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use("TkAgg")


def MakeFile():
	plt.plot(['levels', 'level2', 'level3'],[35, 40, 22], label="levels", marker="o", c="#ff0000")
	plt.plot(['levels', 'level2', 'level3'],[50, 30, 40], label="level2", marker="o", c="#5ba1d7")
	plt.plot(['levels', 'level2', 'level3'],[20, 35, 60], label="level3", marker="o", c="#4af25d")
	plt.xlabel("Category")
	plt.xlabel("Value's ")
	plt.title("Level's Graph")
	plt.ylim([10,100])
	plt.legend()
	plt.show()


if __name__ == "__main__":
	MakeFile()
