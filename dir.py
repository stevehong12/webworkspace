import enum

class Dir(enum.Enum):
    E = (1, 0); S = (0, -1); W = (-1, 0); N = (0, 1)
    #enum 클래스 = 딕셔너리와 유사 모든 값을 가져와서 특정 값을 리턴

    def left(self):
        return {Dir.E: Dir.N, Dir.N: Dir.W, Dir.W: Dir.S, Dir.S: Dir.E}[self]
        # 매핑을 통해서 현재 방향 기준에서 왼쪽 방향 찾기, 아래는 오른쪽 방향 찾기

    def right(self):
        return {Dir.E: Dir.S, Dir.S: Dir.W, Dir.W: Dir.N, Dir.N: Dir.E}[self]

    @property
    def dx(self):
        return self.value[0]
    #x축에 대한 이동량을 반환한다

    @property
    def dy(self):
        return self.value[1]
    #y축에 대한 이동량을 반환한다
