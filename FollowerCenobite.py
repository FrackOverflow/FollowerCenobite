from FC_Presenter import fc_present as fcp

class FollowerCenobite():
    def main(self):
        self.present = fcp()
        self.present.start_ui()
        
if __name__ == "__main__":
    fc = FollowerCenobite()
    fc.main()