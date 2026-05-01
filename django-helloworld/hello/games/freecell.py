from .base import BaseSolitaire

class FreeCell(BaseSolitaire):
    """
    FreeCell Solitaire - All cards visible with 4 free cells for temporary storage.
    Goal: Build complete sequences on foundations.
    """
    
    def setup_board(self):
        self.stock = []
        self.waste = []
        self.free_cells = [None, None, None, None]  # 4 free cells
        self.foundations = [[] for _ in range(4)]  # 4 foundations
        self.tableaus = [[] for _ in range(8)]  # 8 tableau columns

        self.generate_deck(decks=1)

        # Deal all cards face-up to tableau (4 cards per column for first 4, 3 for last 4)
        stock_copy = self.stock.copy()
        self.stock = []
        
        for i, card in enumerate(stock_copy):
            card.is_face_up = True
            column = i % 8
            self.tableaus[column].append(card)

    def is_valid_move_tableau(self, card, destination_tableau):
        """
        Move to tableau: Card must be one rank lower and opposite color.
        Cannot move directly to empty tableau in FreeCell.
        """
        if not card.is_face_up:
            return False
        
        if not destination_tableau:
            return False  # FreeCell doesn't allow empty tableau starts
        
        top_card = destination_tableau[-1]
        card_rank = card.rank
        top_rank = top_card.rank
        
        return (card_rank == top_rank - 1 and 
                card.color != top_card.color)

    def is_valid_move_foundation(self, card, destination_foundation):
        """Move to foundation: Same suit, ascending order from Ace"""
        if not card.is_face_up:
            return False
        
        if not destination_foundation:
            # Foundation empty - only Ace can start
            return card.rank == 1
        
        top_card = destination_foundation[-1]
        return (card.suit == top_card.suit and 
                card.rank == top_card.rank + 1)

    def is_valid_move_free_cell(self, card, free_cell_index):
        """Move to free cell: Any card, but only if cell is empty"""
        if not card.is_face_up:
            return False
        return self.free_cells[free_cell_index] is None

    def move_to_free_cell(self, card, free_cell_index):
        """Place card in a free cell"""
        if self.is_valid_move_free_cell(card, free_cell_index):
            self.free_cells[free_cell_index] = card
            return True
        return False

    def move_from_free_cell(self, free_cell_index):
        """Remove card from free cell"""
        card = self.free_cells[free_cell_index]
        self.free_cells[free_cell_index] = None
        return card

    def check_win_condition(self):
        """Win if all foundations are complete"""
        return all(len(f) == 13 for f in self.foundations)

    def to_dict(self):
        """Convert game state to dictionary for JSON serialization"""
        base_dict = super().to_dict()
        base_dict['variant'] = 'FreeCell'
        base_dict['num_tableaus'] = 8
        base_dict['free_cells'] = [
            card.to_dict() if card else None 
            for card in self.free_cells
        ]
        return base_dict
