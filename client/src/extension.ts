// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as net from "net";
import * as path from "path";
import * as vscode from 'vscode';
import * as cp from "child_process";

import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient";
import { ENGINE_METHOD_PKEY_ASN1_METHS, EIDRM } from "constants";

let client: LanguageClient;
let PROCESS: cp.ChildProcess;

function getClientOptions(): LanguageClientOptions {
	vscode.window.activeTextEditor?.document
	return {
	 	 // Register the server for plain text documents
		documentSelector: [
			{ scheme: "file", language: "plaintext"},
		],
		outputChannelName: "[pygls] DRC Language Server",
		synchronize: {
			// Notify the server about file changes to '.clientrc files contain in the workspace
			fileEvents: vscode.workspace.createFileSystemWatcher("**/.clientrc"),
		},
	};
}

function startLangServerTCP(addr: number): LanguageClient {
	const serverOptions: ServerOptions = () => {
		return new Promise((resolve, reject) => {
				const clientSocket = new net.Socket();
				clientSocket.connect(addr, "127.0.0.1", () => {
				resolve({
					reader: clientSocket,
					writer: clientSocket,
				});
			});
		});
	};

	return new LanguageClient(`tcp lang server (port ${addr})`, serverOptions, getClientOptions());
}

function startLangServer(
	command: string, args: string[], cwd: string,
  ): LanguageClient {
	const serverOptions: ServerOptions = {
	  args,
	  command,
	  options: { cwd },
	};

	return new LanguageClient(command, serverOptions, getClientOptions());
  }

function isStartedInDebugMode(): boolean {
	return true;
	// return process.env.VSCODE_DEBUG_MODE === "true";
}

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
	vscode.commands.registerCommand("extension.test", () => {
		console.log('test vscode');
		console.log(vscode.window.activeTextEditor?.selection);
		vscode.window.activeTextEditor?.edit((edit) => {
			const p = new vscode.Position(0, 0);
			edit.insert(p, "baer");
		});
		let p1 = new vscode.Position(0,0);
		let p2 = new vscode.Position(0,5);
		let text = new vscode.Selection(p1, p2);
	});
	vscode.window.onDidChangeTextEditorSelection( (event)=> {
		console.log(event);
		vscode.window.setStatusBarMessage("hi");
	});
	let root = context.extensionPath;
	if (isStartedInDebugMode()) {
		client = startLangServerTCP(2087);
	} else {
		const cwd = path.join(__dirname, "..", "..");
		const pythonPath = vscode.workspace.getConfiguration("python").get<string>("pythonPath");

		if (!pythonPath) {
			throw new Error("`python.pythonPath` is not set");
		}

		client = startLangServer(`${root}/dist/drc-language-server`, [], cwd);
		
	// 	//client = startLangServer(pythonPath, ["-m", "server"], cwd);
	}
	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "drc-language-server" is now active!');
	context.subscriptions.push(client.start());
}

// this method is called when your extension is deactivated
export function deactivate() {
	if (PROCESS) {
		PROCESS.kill('SIGHUP');
	}
	return client ? client.stop() : Promise.resolve();
}
