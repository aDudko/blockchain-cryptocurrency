<template>
    <div>
        <div class="container">
            <div class="row mb-3">
                <div class="col">
                    <h1>Manage your Blockchain</h1>
                </div>
            </div>
            <div v-if="error" class="alert alert-danger" role="alert">
                {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
                {{ success }}
            </div>
            <div class="row">
                <div class="col">
                    <div v-if="!walletLoading">
                        <button class="btn btn-primary" @click="onCreateWallet">
                            Create new Wallet
                        </button>
                        <button class="btn btn-primary" @click="onLoadWallet">
                            Load Wallet
                        </button>
                    </div>

                    <div v-if="walletLoading" class="lds-ring">
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>
                </div>
                <div class="col text-right">
                    <h2>Funds: {{ funds.toFixed(2) }}</h2>
                </div>
            </div>
            <hr>
            <div v-if="!wallet" class="row">
                <div class="col">
                    <div class="alert alert-warning">Create a Wallet to start sending coins or to mine coins!</div>
                </div>
            </div>
            <div v-if="wallet" class="row">
                <div class="col">
                    <form @submit.prevent="onSendTx">
                        <div class="form-group">
                            <label for="recipient">Recipient Key</label>
                            <input v-model="outgoingTx.recipient" type="text" class="form-control" id="recipient" placeholder="Enter key">
                        </div>
                        <div class="form-group">
                            <label for="amount">Amount of Coins</label>
                            <input v-model.number="outgoingTx.amount" type="number" step="0.001" class="form-control" id="amount">
                            <small class="form-text text-muted">Fractions are possible (e.g. 5.67)</small>
                        </div>
                        <div v-if="txLoading" class="lds-ring">
                            <div></div>
                            <div></div>
                            <div></div>
                            <div></div>
                        </div>
                        <button
                            :disabled="txLoading || outgoingTx.recipient.trim() === '' || outgoingTx.amount <= 0"
                            type="submit" class="btn btn-primary">Send
                        </button>
                    </form>
                </div>
            </div>
            <hr>
            <div class="row">
                <div class="col">
                    <ul class="nav nav-tabs">
                        <li class="nav-item">
                            <a class="nav-link" :class="{active: view === 'chain'}" href="#" @click="view = 'chain'">Blockchain</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" :class="{active: view === 'tx'}" href="#" @click="view = 'tx'">Open Transactions</a>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="row my-3">
                <div class="col">
                    <button class="btn btn-primary" @click="onLoadData">
                        {{ view === 'chain' ? 'Load Blockchain' : 'Load Transactions' }}
                    </button>
                    <button v-if="view === 'chain' && wallet" class="btn btn-success" @click="onMine">Mine Coins</button>
                    <button class="btn btn-warning" @click="onResolve">Resolve Conflicts</button>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <div v-if="dataLoading" class="lds-ring">
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>
                    <div v-if="!dataLoading" class="accordion">
                        <div class="card" v-for="(data, index) in loadedData" :key="index">
                            <div v-if="view === 'chain'" class="card-header">
                                <h5 class="mb-0">
                                    <button class="btn btn-link" type="button"
                                            @click="showElement === index ? showElement = null : showElement = index">
                                        Block #{{ data.index }}
                                    </button>
                                </h5>
                            </div>
                            <div v-if="view === 'chain'" class="collapse" :class="{show: showElement === index}">
                                <div class="card-body">
                                    <p>Previous Hash: {{ data.previous_hash }}</p>
                                    <div class="list-group">
                                        <div v-for="tx in data.transactions"
                                             class="list-group-item flex-column align-items-start">
                                            <div>Sender: {{ tx.sender }}</div>
                                            <div>Recipient: {{ tx.recipient }}</div>
                                            <div>Amount: {{ tx.amount }}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div v-if="view === 'tx'" class="card-header">
                                <h5 class="mb-0">
                                    <button class="btn btn-link" type="button"
                                            @click="showElement === index ? showElement = null : showElement = index">
                                        Transaction #{{ index }}
                                    </button>
                                </h5>
                            </div>
                            <div v-if="view === 'tx'" class="collapse" :class="{show: showElement === index}">
                                <div class="card-body">
                                    <div class="list-group">
                                        <div class="list-group-item flex-column align-items-start">
                                            <div>Sender: {{ data.sender }}</div>
                                            <div>Recipient: {{ data.recipient }}</div>
                                            <div>Amount: {{ data.amount }}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {
    data() {
        return {
            blockchain: [],
            openTransactions: [],
            wallet: null,
            view: "chain",
            walletLoading: false,
            txLoading: false,
            dataLoading: false,
            showElement: null,
            error: null,
            success: null,
            funds: 0,
            outgoingTx: {
                recipient: "",
                amount: 0,
            },
        };
    },
    computed: {
        loadedData() {
            return this.view === "chain" ? this.blockchain : this.openTransactions;
        },
    },
    methods: {
        async onCreateWallet() {
            this.walletLoading = true;
            try {
                const response = await axios.post("/wallet");
                this.error = null;
                this.success = "Wallet was created.";
                this.wallet = {
                    public_key: response.data.public_key,
                    private_key: response.data.private_key,
                };
                this.funds = response.data.funds;
            } catch (error) {
                this.error = error.response.data.message;
                this.success = null;
                this.wallet = null;
            } finally {
                this.walletLoading = false;
            }
        },
        async onLoadWallet() {
            this.walletLoading = true;
            try {
                const response = await axios.get("/wallet");
                this.error = null;
                this.success = "Wallet was loaded.";
                this.wallet = {
                    public_key: response.data.public_key,
                    private_key: response.data.private_key,
                };
                this.funds = response.data.funds;
            } catch (error) {
                this.error = error.response.data.message;
                this.success = null;
                this.wallet = null;
            } finally {
                this.walletLoading = false;
            }
        },
        async onSendTx() {
            this.txLoading = true;
            try {
                const response = await axios.post("/transaction", {
                    recipient: this.outgoingTx.recipient,
                    amount: this.outgoingTx.amount,
                });
                this.error = null;
                this.success = response.data.message;
                this.funds = response.data.funds;
            } catch (error) {
                this.error = error.response.data.message;
                this.success = null;
            } finally {
                this.txLoading = false;
            }
        },
        async onMine() {
            try {
                const response = await axios.post("/mine");
                this.error = null;
                this.success = response.data.message;
                this.funds = response.data.funds;
            } catch (error) {
                this.error = error.response.data.message;
                this.success = null;
            }
        },
        async onLoadData() {
            if (this.view === "chain") {
                const response = await axios.get("/chain");
                this.blockchain = response.data;
            } else {
                const response = await axios.get("/transactions");
                this.openTransactions = response.data;
            }
        },
        async onResolve() {
            try {
                const response = await axios.post("/resolve-conflicts");
                this.error = null;
                this.success = response.data.message;
            } catch (error) {
                this.error = error.response.data.message;
                this.success = null;
            }
        },
    },
};
</script>