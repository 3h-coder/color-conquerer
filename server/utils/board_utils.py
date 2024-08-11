from dto.cell_info_dto import CellInfoDto


def display_board_owners(board: list[list[CellInfoDto]]):
    for row in board:
        row_display = "|".join(str(cell.owner) for cell in row)
        print(f"|{row_display}|")
        print("_" * (2 * len(row)))
