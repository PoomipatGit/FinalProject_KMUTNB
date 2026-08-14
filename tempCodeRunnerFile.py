	def __init__(self, parent, controller):
		# 1. Mount as a tk.Frame child inside master container
		super().__init__(parent, controller)
		self.controller = controller