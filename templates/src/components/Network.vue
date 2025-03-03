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
                    <form @submit.prevent="onAddNode">
                        <div class="form-group">
                            <label for="node-url">Node URL</label>
                            <input v-model="newNodeUrl" type="text" class="form-control" id="node-url" placeholder="node-1">
                        </div>
                        <button :disabled="newNodeUrl.trim() === ''" type="submit" class="btn btn-primary">Add</button>
                    </form>
                </div>
            </div>
            <hr>
            <div class="row my-3">
                <div class="col">
                    <button class="btn btn-primary" @click="onLoadNodes">Load Peer Nodes</button>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <ul class="list-group">
                        <button
                            v-for="node in nodes"
                            :key="node"
                            style="cursor: pointer;"
                            class="list-group-item list-group-item-action"
                            @click="onRemoveNode(node)">
                            {{ node }} (click to delete)
                        </button>
                    </ul>
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
            nodes: [],
            newNodeUrl: "",
            error: null,
            success: null,
        };
    },
    methods: {
        async onAddNode() {
            try {
                const response = await axios.post("/node", { node: this.newNodeUrl });
                this.success = "Store node successfully.";
                this.error = null;
                this.nodes = response.data.all_nodes;
            } catch (error) {
                this.success = null;
                this.error = error.response.data.message;
            }
        },
        async onLoadNodes() {
            try {
                const response = await axios.get("/node");
                this.success = "Fetched nodes successfully.";
                this.error = null;
                this.nodes = response.data.all_nodes;
            } catch (error) {
                this.success = null;
                this.error = error.response.data.message;
            }
        },
        async onRemoveNode(node_url) {
            try {
                const response = await axios.delete(`/node/${node_url}`);
                this.success = "Deleted node successfully.";
                this.error = null;
                this.nodes = response.data.all_nodes;
            } catch (error) {
                this.success = null;
                this.error = error.response.data.message;
            }
        },
    },
};
</script>