class FpsCounter:
    NB_SAMPLE = 30

    def __init__(self):
        self.fps_data = [0]*FpsCounter.NB_SAMPLE
        self.next_sample_indice = 0

    def update(self, fps_sample):
        self.fps_data[self.next_sample_indice] = fps_sample
        self.next_sample_indice = (self.next_sample_indice+1) % FpsCounter.NB_SAMPLE

    def get_fps(self):
        n = sum(self.fps_data) / FpsCounter.NB_SAMPLE
        if n == 0.0:
            return 0.0
        return 1.0 / n
