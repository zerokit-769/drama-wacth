const fs = require('fs');
const os = require('os');
const readline = require('readline');
const { Wallet } = require('ethers');

if (!process.env.PREFIX || !process.env.PREFIX.includes('com.termux')) {
    console.log("❌ Access Denied: This script can only be run in Termux.");
    process.exit(1);
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const wallets = [];

const colors = {
    reset: '\x1b[0m',
    cyan: '\x1b[36m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    white: '\x1b[37m',
    bold: '\x1b[1m'
};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function clearLine() {
    process.stdout.write('\r\x1b[K');
}

async function loadingAnimation(total) {
    const frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];

    for (let i = 0; i < total; i++) {
        const wallet = Wallet.createRandom();

        wallets.push({
            address: wallet.address,
            privateKey: wallet.privateKey,
            mnemonic: wallet.mnemonic.phrase
        });

        const frame = frames[i % frames.length];
        const percent = Math.floor(((i + 1) / total) * 100);

        process.stdout.write(
            `\r${colors.cyan}${frame}${colors.reset} ` +
            `${colors.bold}Generating EVM Wallets${colors.reset} ` +
            `${colors.yellow}[${i + 1}/${total}]${colors.reset} ` +
            `${colors.green}${percent}%${colors.reset}`
        );

        await sleep(15);
    }

    clearLine();
}

console.clear();

console.log(
    `\n${colors.cyan}${colors.bold}🔐 GENERATED ADDRESS EVM WALLET${colors.reset}\n`
);

rl.question(
    `${colors.magenta}◆${colors.reset} ${colors.white}How many wallets do you want to create? ${colors.reset}`,
    async (answer) => {
        const count = parseInt(answer.trim(), 10);

        if (!Number.isInteger(count) || count <= 0) {
            console.log(
                `\n${colors.yellow}⚠️  Invalid wallet amount.${colors.reset}`
            );
            rl.close();
            process.exit(1);
        }

        console.log(
            `\n${colors.blue}ℹ${colors.reset} ` +
            `${colors.white}Preparing to generate ${count} EVM wallet(s)...${colors.reset}\n`
        );

        await loadingAnimation(count);

        fs.writeFileSync(
            'bnb.json',
            JSON.stringify(wallets, null, 4)
        );

        console.log(
            `${colors.green}✔${colors.reset} ` +
            `${colors.bold}Successfully generated ${count} EVM wallet(s).${colors.reset}`
        );

        console.log(
            `${colors.cyan}📁${colors.reset} ` +
            `${colors.white}Saved to:${colors.reset} ${colors.yellow}bnb.json${colors.reset}\n`
        );

        rl.close();
    }
);