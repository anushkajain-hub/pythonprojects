#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <windows.h>
#include <conio.h>

#define SIZE 25
#define MAX_HISTORY 5
#define MAX_LEADERBOARD 5

char grid[SIZE][SIZE];

int playerX, playerY;
int exitX = SIZE - 1;
int exitY = SIZE - 1;

int lives;
int timeCount;
int level;
int fireDelay;
int fireChance;
int theme = 1;
int highScore = 0;

int scoreHistory[MAX_HISTORY];
int historyCount = 0;
int leaderboard[MAX_LEADERBOARD];
int leaderCount = 0;


#define GRID_TOP 4



void setConsoleWidth() {
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    
    COORD buf = {52, 200};
    SetConsoleScreenBufferSize(h, buf);
    SMALL_RECT win = {0, 0, 51, 40};
    SetConsoleWindowInfo(h, TRUE, &win);
}

void hideCursor() {
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_CURSOR_INFO info;
    info.dwSize = 100;
    info.bVisible = FALSE;
    SetConsoleCursorInfo(h, &info);
}

void showCursor() {
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_CURSOR_INFO info;
    info.dwSize = 100;
    info.bVisible = TRUE;
    SetConsoleCursorInfo(h, &info);
}

void gotoxy(int x, int y) {
    COORD c; c.X = x; c.Y = y;
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), c);
}

void setColor(int c) {
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), c);
}

void applyTheme() {
    if (theme == 1) system("color 0F");
    if (theme == 2) system("color 0A");
    if (theme == 3) system("color 04");
}


void drawCell(int row, int col) {
    gotoxy(col * 2, GRID_TOP + row);
    if (row == playerX && col == playerY)  { setColor(10); printf("@ "); }
    else if (row == exitX && col == exitY) { setColor(9);  printf("X "); }
    else if (grid[row][col] == '*')        { setColor(12); printf("* "); }
    else if (grid[row][col] == '#')        { setColor(8);  printf("# "); }
    else                                   { setColor(7);  printf(". "); }
    setColor(7);
}


void updateStats() {
    gotoxy(0, 1);
    setColor(7);
    printf("Lives:%d  Level:%d  Time:%-6d  Score:%-6d",
           lives, level, timeCount, timeCount * level);
}


int getValidInt(int min, int max) {
    char buffer[50];
    int value;
    char extra;
    if (fgets(buffer, sizeof(buffer), stdin) == NULL) return -1;
    buffer[strcspn(buffer, "\n")] = '\0';
    if (strlen(buffer) == 0) return -1;
    if (sscanf(buffer, "%d%c", &value, &extra) != 1) return -1;
    if (value < min || value > max) return -1;
    return value;
}



void loadHighScore() {
    FILE *f = fopen("highscore.txt", "r");
    if (f) { fscanf(f, "%d", &highScore); fclose(f); }
}

void saveHighScore(int score) {
    if (score > highScore) {
        highScore = score;
        FILE *f = fopen("highscore.txt", "w");
        fprintf(f, "%d", score);
        fclose(f);
    }
}

void loadHistory() {
    FILE *f = fopen("history.txt", "r");
    historyCount = 0;
    if (f) {
        while (fscanf(f, "%d", &scoreHistory[historyCount]) != EOF && historyCount < MAX_HISTORY)
            historyCount++;
        fclose(f);
    }
}

void saveHistory(int score) {
    if (historyCount < MAX_HISTORY)
        scoreHistory[historyCount++] = score;
    else {
        for (int i = 1; i < MAX_HISTORY; i++) scoreHistory[i-1] = scoreHistory[i];
        scoreHistory[MAX_HISTORY-1] = score;
    }
    FILE *f = fopen("history.txt", "w");
    for (int i = 0; i < historyCount; i++) fprintf(f, "%d\n", scoreHistory[i]);
    fclose(f);
}

void loadLeaderboard() {
    FILE *f = fopen("leaderboard.txt", "r");
    leaderCount = 0;
    if (f) {
        while (fscanf(f, "%d", &leaderboard[leaderCount]) != EOF && leaderCount < MAX_LEADERBOARD)
            leaderCount++;
        fclose(f);
    }
}

void saveLeaderboard(int score) {
    leaderboard[leaderCount++] = score;
    for (int i = 0; i < leaderCount; i++)
        for (int j = i+1; j < leaderCount; j++)
            if (leaderboard[j] > leaderboard[i]) {
                int t = leaderboard[i]; leaderboard[i] = leaderboard[j]; leaderboard[j] = t;
            }
    if (leaderCount > MAX_LEADERBOARD) leaderCount = MAX_LEADERBOARD;
    FILE *f = fopen("leaderboard.txt", "w");
    for (int i = 0; i < leaderCount; i++) fprintf(f, "%d\n", leaderboard[i]);
    fclose(f);
}


void menu();
void startGame();



void showResult(int won) {
    int score = timeCount * level;
    saveHighScore(score);
    saveHistory(score);
    saveLeaderboard(score);

    system("cls");
    showCursor();
    setConsoleWidth();

    setColor(14);
    printf("\n\n");
    if (won)
        printf("  *** YOU ESCAPED! ***\n");
    else
        printf("  *** GAME OVER ***\n");
    printf("\n");
    setColor(7);
    printf("  Your Score : %d\n", score);
    printf("  High Score : %d\n", highScore);
    printf("\n");
    setColor(11);
    printf("  1. Main Menu\n");
    printf("  2. Exit\n");
    printf("\n");
    setColor(7);
    printf("  Choose: ");

    int choice = -1;
    while (choice == -1) {
        choice = getValidInt(1, 2);
        if (choice == -1) { setColor(12); printf("  Invalid! Enter 1 or 2: "); setColor(7); }
    }

    if (choice == 1) menu();
    else exit(0);
}



void setLevel() {
    int choice = -1;
    while (choice == -1) {
        printf("\nSelect Difficulty:\n1. Easy\n2. Medium\n3. Hard\nEnter choice: ");
        choice = getValidInt(1, 3);
        if (choice == -1) { setColor(12); printf("  Invalid input! Enter 1, 2, or 3.\n"); setColor(7); }
    }
    level = choice;
    if (level == 1)      { fireDelay = 15; fireChance = 20; }
    else if (level == 2) { fireDelay = 8;  fireChance = 30; }
    else                 { fireDelay = 4;  fireChance = 45; }
}

void initializeGrid() {
    for (int i = 0; i < SIZE; i++)
        for (int j = 0; j < SIZE; j++)
            grid[i][j] = '.';
    playerX = 0; playerY = 0;
}

void placeWalls() {
    for (int i = 0; i < 80; i++) {
        int x = rand() % SIZE, y = rand() % SIZE;
        if ((x != 0 || y != 0) && (x != exitX || y != exitY))
            grid[x][y] = '#';
    }
}

void placeFire() {
    int x, y;
    do { x = rand() % SIZE; y = rand() % SIZE; }
    while (grid[x][y] != '.' || (x==0&&y==0) || (x==exitX&&y==exitY));
    grid[x][y] = '*';
}



void drawAll() {
    system("cls");
    hideCursor();

    /* header - 4 lines (rows 0-3) */
    gotoxy(0, 0); printf("========= FIRE ESCAPE GAME =========");
    gotoxy(0, 1); printf("Lives:%d  Level:%d  Time:%-6d  Score:%-6d", lives, level, timeCount, timeCount*level);
    gotoxy(0, 2); printf("High Score:%-6d", highScore);
    gotoxy(0, 3); printf("------------------------------------");

    
    for (int i = 0; i < SIZE; i++)
        for (int j = 0; j < SIZE; j++)
            drawCell(i, j);

    
    gotoxy(0, GRID_TOP + SIZE);
    setColor(7);
    printf("Controls: W A S D");
}



void spreadFire() {
    char temp[SIZE][SIZE];
    for (int i = 0; i < SIZE; i++)
        for (int j = 0; j < SIZE; j++)
            temp[i][j] = grid[i][j];

    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            if (grid[i][j] == '*') {
                if (rand()%100 < fireChance && i+1 < SIZE && grid[i+1][j]=='.') temp[i+1][j]='*';
                if (rand()%100 < fireChance && i-1 >= 0   && grid[i-1][j]=='.') temp[i-1][j]='*';
                if (rand()%100 < fireChance && j+1 < SIZE && grid[i][j+1]=='.') temp[i][j+1]='*';
                if (rand()%100 < fireChance && j-1 >= 0   && grid[i][j-1]=='.') temp[i][j-1]='*';
            }
        }
    }

   
    for (int i = 0; i < SIZE; i++)
        for (int j = 0; j < SIZE; j++)
            if (temp[i][j] != grid[i][j]) {
                grid[i][j] = temp[i][j];
                drawCell(i, j);
            }

    Beep(1000, 50);
}



void movePlayer(char ch) {
    int oldX = playerX, oldY = playerY;
    int nx = playerX, ny = playerY;

    if (ch == 'w') nx--;
    if (ch == 's') nx++;
    if (ch == 'a') ny--;
    if (ch == 'd') ny++;

    if (nx >= 0 && nx < SIZE && ny >= 0 && ny < SIZE && grid[nx][ny] != '#') {
        playerX = nx; playerY = ny;
    }

    drawCell(oldX, oldY);
    drawCell(playerX, playerY);

    if (grid[playerX][playerY] == '*') {
        lives--;
        Beep(400, 300);
        playerX = 0; playerY = 0;
        drawCell(oldX, oldY);
        drawCell(0, 0);
        updateStats();
    }

    if (playerX == exitX && playerY == exitY) showResult(1);
    if (lives <= 0) showResult(0);
}



void menu() {
    showCursor();
    
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    COORD buf = {120, 200};
    SetConsoleScreenBufferSize(h, buf);
    SMALL_RECT win = {0, 0, 79, 24};
    SetConsoleWindowInfo(h, TRUE, &win);

    int choice = -1;
    system("cls");
    while (choice == -1) {
        printf("====== FIRE ESCAPE GAME ======\n");
        printf("1. Start Game\n2. Change Theme\n3. Exit\n");
        printf("Choose: ");
        choice = getValidInt(1, 3);
        if (choice == -1) {
            setColor(12); printf("  Invalid input! Enter 1, 2, or 3.\n"); setColor(7);
            Sleep(900); system("cls");
        }
    }
    if (choice == 2) {
        int themeChoice = -1;
        while (themeChoice == -1) {
            printf("1. Classic\n2. Green\n3. Danger\nChoose theme: ");
            themeChoice = getValidInt(1, 3);
            if (themeChoice == -1) { setColor(12); printf("  Invalid input!\n"); setColor(7); }
        }
        theme = themeChoice;
        applyTheme();
        menu();
    }
    if (choice == 3) exit(0);
    if (choice == 1) startGame();
}



void startGame() {
    setLevel();
    applyTheme();

    lives = 3;
    timeCount = 0;

    initializeGrid();
    placeWalls();
    placeFire();

    
    setConsoleWidth();

    drawAll(); 

    int fireCounter = 0;

    while (1) {
        if (kbhit())
            movePlayer(getch());

        fireCounter++;
        if (fireCounter >= fireDelay) {
            spreadFire();
            fireCounter = 0;
        }

        if (timeCount % 300 == 0 && timeCount > 0 && level < 5) {
            level++;
            fireChance += 5;
            fireDelay--;
        }

        
        updateStats();

        Sleep(120);
        timeCount++;
    }
}



int main() {
    srand(time(0));
    loadHighScore();
    loadHistory();
    loadLeaderboard();
    menu();
    return 0;
}
