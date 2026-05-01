document.addEventListener('DOMContentLoaded', () => {
    const dataScript = document.getElementById('solitaire-data');
    if (!dataScript) {
        initializeDragAndDrop();
        return;
    }

    const gameData = JSON.parse(dataScript.textContent);
    let stockCards = gameData.stock || [];
    let wasteCards = gameData.waste || [];
    const stockPile = document.getElementById('stock-pile');
    const wastePile = document.getElementById('waste-pile');
    const drawButton = document.getElementById('draw-button');
    const stockStatus = document.getElementById('stock-status');

    const createCardElement = (card) => {
        const cardEl = document.createElement('div');
        cardEl.className = `card ${card.color.toLowerCase()}`;
        cardEl.draggable = true;
        cardEl.dataset.rank = card.rank;
        cardEl.dataset.suit = card.suit;
        cardEl.dataset.color = card.color.toLowerCase();
        cardEl.dataset.faceUp = 'true';
        cardEl.textContent = `${card.rank_display} ${card.suit_symbol}`;
        return cardEl;
    };

    const renderWaste = () => {
        wastePile.innerHTML = '';
        if (wasteCards.length === 0) {
            wastePile.innerHTML = '<div class="empty-card">Waste</div>';
            return;
        }
        wasteCards.forEach(card => {
            wastePile.appendChild(createCardElement(card));
        });
        initializeDragAndDrop();
    };

    const updateStockCount = () => {
        const countEl = document.querySelector('.stock-count');
        if (!countEl) return;
        countEl.textContent = stockCards.length;
        if (stockCards.length === 0) {
            stockPile.innerHTML = '<div class="empty-card">No Stock</div>';
        }
        if (stockStatus) {
            stockStatus.textContent = `Stock: ${stockCards.length}`;
        }
    };

    const drawCard = () => {
        if (stockCards.length === 0) return;

        const gameVariant = document.body.dataset.variant;

        if (gameVariant === 'Spider') {
            const tableauColumns = document.querySelectorAll('.pile.tableau');
            if (stockCards.length >= tableauColumns.length) {
                tableauColumns.forEach(column => {
                    const cardData = stockCards.pop();
                    cardData.is_face_up = true;
                    const emptyPlaceholder = column.querySelector('.empty-card');
                    if (emptyPlaceholder) emptyPlaceholder.remove();
                    column.appendChild(createCardElement(cardData));
                });
                updateStockCount();
                initializeDragAndDrop();
                moveCount++; 
            } else {
                console.log("Not enough cards in stock to deal Spider row.");
            }
        } else {
            const card = stockCards.pop();
            card.is_face_up = true;
            wasteCards.push(card);
            renderWaste();
            updateStockCount();
            moveCount++; 
        }
    };

    drawButton?.addEventListener('click', drawCard);
    stockPile?.addEventListener('click', drawCard);
    
    if (document.body.dataset.variant !== 'Spider') {
        renderWaste();
    }
    
    updateStockCount();
    initializeDragAndDrop();
});

let moveCount = 0;
let draggedCard = null;
let draggedCards = [];
let originalParent = null;

function initializeDragAndDrop() {
    const cards = document.querySelectorAll('.card[draggable="true"]');
    const piles = document.querySelectorAll('.pile');

    cards.forEach(card => {
        card.removeEventListener('dragstart', dragStart);
        card.removeEventListener('dragend', dragEnd);
        card.addEventListener('dragstart', dragStart);
        card.addEventListener('dragend', dragEnd);
    });

    piles.forEach(pile => {
        pile.removeEventListener('dragover', dragOver);
        pile.removeEventListener('dragenter', dragEnter);
        pile.removeEventListener('dragleave', dragLeave);
        pile.removeEventListener('drop', dragDrop);
        pile.addEventListener('dragover', dragOver);
        pile.addEventListener('dragenter', dragEnter);
        pile.addEventListener('dragleave', dragLeave);
        pile.addEventListener('drop', dragDrop);
    });
}

function dragStart(e) {
    if (this.dataset.faceUp !== 'true' || this.classList.contains('face-down')) {
        e.preventDefault();
        return;
    }

    draggedCard = this;
    originalParent = this.parentElement;
    draggedCards = [this];
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', 'solitaire-card');

    let nextSibling = this.nextElementSibling;
    while (nextSibling && nextSibling.classList.contains('card')) {
        draggedCards.push(nextSibling);
        nextSibling = nextSibling.nextElementSibling;
    }

    draggedCards.forEach(card => card.classList.add('dragging'));
}

function dragEnd(e) {
    draggedCards.forEach(card => card.classList.remove('dragging'));
    draggedCard = null;
    draggedCards = [];
}

function dragOver(e) {
    e.preventDefault(); 
    if (e.dataTransfer) {
        e.dataTransfer.dropEffect = 'move';
    }
}

function dragEnter(e) {
    e.preventDefault();
    const destination = getDropDestination(e.target);
    if (destination) {
        destination.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
    }
}

function dragLeave(e) {
    const destination = getDropDestination(e.target);
    if (destination) {
        destination.style.backgroundColor = 'transparent';
    }
}

function dragDrop(e) {
    e.preventDefault();
    const destination = getDropDestination(e.target);
    if (!destination) {
        invalidMove();
        return;
    }
    destination.style.backgroundColor = 'transparent';

    const destinationType = destination.dataset.pileType;
    if (!draggedCard || !destinationType || destinationType === 'stock' || destinationType === 'waste') {
        invalidMove();
        return;
    }

    const targetCard = findTopCard(destination);
    if (isValidMove(draggedCard, destinationType, targetCard)) {
        
        const emptyPlaceholder = destination.querySelector('.empty-card');
        if (emptyPlaceholder) emptyPlaceholder.remove();

        draggedCards.forEach(card => destination.appendChild(card));
        revealNextFaceDownCard(originalParent);
        
        moveCount++;
        checkWinCondition();
        
    } else {
        invalidMove();
    }
}

function revealNextFaceDownCard(pile) {
    if (!pile || pile.dataset.pileType !== 'tableau') return;

    const cards = Array.from(pile.querySelectorAll('.card'));
    if (!cards.length) {
        pile.innerHTML = '<div class="empty-card">Empty</div>';
        return;
    }

    const lastCard = cards[cards.length - 1];
    if (lastCard.dataset.faceUp === 'false' || lastCard.classList.contains('face-down')) {
        lastCard.dataset.faceUp = 'true';
        lastCard.draggable = true;
        lastCard.classList.remove('face-down');
        lastCard.textContent = `${getRankDisplay(lastCard.dataset.rank)} ${getSuitSymbol(lastCard.dataset.suit)}`;
        initializeDragAndDrop();
    }
}

function getRankDisplay(rank) {
    const parsed = parseInt(rank, 10);
    return {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}[parsed] || String(parsed);
}

function getSuitSymbol(suit) {
    return {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}[suit] || suit;
}

function getDropDestination(target) {
    if (!target) return null;
    if (target.classList.contains('pile')) return target;
    return target.closest('.pile');
}

function findTopCard(pile) {
    const cards = Array.from(pile.querySelectorAll('.card'));
    return cards.length ? cards[cards.length - 1] : null;
}

function isValidMove(card, destinationType, topCard) {
    if (!card || card.dataset.faceUp !== 'true') return false;

    const cardRank = parseInt(card.dataset.rank, 10);
    const cardSuit = card.dataset.suit;
    const cardColor = card.dataset.color;

    if (destinationType === 'freecell') {
        if (draggedCards.length > 1) return false; 
        if (topCard) return false; 
        return true; 
    }

    if (destinationType === 'foundation') {
        if (draggedCards.length > 1) return false; 
        if (!topCard) return cardRank === 1;
        const topRank = parseInt(topCard.dataset.rank, 10);
        const topSuit = topCard.dataset.suit;
        return topSuit === cardSuit && cardRank === topRank + 1;
    }

    if (destinationType === 'tableau') {
        const gameVariant = document.body.dataset.variant;
        if (!topCard) return cardRank === 13; 
        
        const topRank = parseInt(topCard.dataset.rank, 10);
        
        if (gameVariant === 'Spider') {
            return cardRank === topRank - 1;
        }

        const topColor = topCard.dataset.color;
        return topColor !== cardColor && cardRank === topRank - 1;
    }
    return false;
}

function invalidMove() {
    if (originalParent && draggedCards.length > 0) {
        draggedCards.forEach(card => originalParent.appendChild(card));
    }
    draggedCard = null;
    draggedCards = [];
}

// --- WIN CHECK & API SAVE ---
function checkWinCondition() {
    const foundations = document.querySelectorAll('.pile[data-pile-type="foundation"]');
    let totalCardsInFoundations = 0;
    
    const gameVariant = document.body.dataset.variant;
    const requiredCards = (gameVariant === 'Spider') ? 104 : 52;

    foundations.forEach(foundation => {
        totalCardsInFoundations += foundation.querySelectorAll('.card').length;
    });

    if (totalCardsInFoundations === requiredCards) {
        alert(`🎉 You won in ${moveCount} moves! Saving your score to the leaderboard...`);
        saveGameResult(true);
    }
}

function saveGameResult(isWon) {
    const sessionId = document.body.dataset.sessionId;
    if (!sessionId) {
        console.error("No session ID found, cannot save game.");
        return;
    }

    const score = Math.max(0, 5000 - (moveCount * 10));

    fetch('/api/save-game-result/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            session_id: sessionId,
            is_won: isWon,
            score: score,
            moves: moveCount
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            window.location.href = '/statistics/';
        } else {
            console.error("Failed to save game:", data.message);
        }
    })
    .catch(error => console.error("Error saving game:", error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}