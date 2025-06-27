<script lang="ts">
	import CodeMirror from 'svelte-codemirror-editor';
	import { oneDark } from '@codemirror/theme-one-dark';
	import { LanguageSupport, StreamLanguage } from '@codemirror/language';
	import { html } from '@codemirror/lang-html';
	import { PUBLIC_COMMIT_SHA } from '$env/static/public';
	import { IconGitCommit, IconWifi, IconWifiOff } from '@tabler/icons-svelte';
	import { gitRepoUrl } from '$lib';
	import { onMount } from 'svelte';

	let value = $state(`!html!
html[lang="en"] {
  head {
    meta[charset="UTF-8"].
    title "My First Web Page"
  }
  body[style="background-color: #dddddd"] {
    <# This is a comment #>
    h1 "Welcome to My Web Page"
    p "This is a simple BTML example with a button below."
    button[onclick="alert('Hello, world!')"] "Click Me"
  }
}`);

	const btmlLanguage = StreamLanguage.define({
		name: 'btml',
		token(stream, state) {
			// DOCTYPE declarations
			if (stream.match(/^!/)) {
				stream.skipTo('!');
				stream.match(/!/);
				return 'string-2';
			}

			// BTML comments <# ... #>
			if (stream.match(/^<#/)) {
				stream.skipTo('#>');
				stream.match(/#>/);
				return 'comment';
			}

			// Atoms (true, false, null)
			if (stream.match(/^(true|false|null)\b/)) {
				return 'atom';
			}

			// Numbers (integers and floats)
			if (stream.match(/^\d+(\.\d+)?/)) {
				return 'number';
			}

			// Any HTML tag name
			if (stream.match(/^[a-zA-Z][a-zA-Z0-9-]*(?=[\s\[\{]|.$)/)) {
				return 'tag';
			}

			// Attribute names and values inside brackets
			if (stream.match(/^\[/)) {
				return 'bracket';
			}
			// Handle closing bracket
			if (stream.match(/^\]/)) {
				return 'bracket';
			}
			if (stream.match(/^[a-zA-Z-]+(?==)/)) {
				return 'attribute';
			}

			// Strings in quotes
			if (stream.match(/^"([^"\\]|\\.)*"/)) {
				return 'string';
			}
			if (stream.match(/^'([^'\\]|\\.)*'/)) {
				return 'string';
			}

			// Braces
			if (stream.match(/^[{}]/)) {
				return 'bracket';
			}

			// Dots for self-closing tags
			if (stream.match(/^\./)) {
				return 'operator';
			}

			stream.next();
			return null;
		}
	});

	const btmlSupport = new LanguageSupport(btmlLanguage);

	const commitSha = PUBLIC_COMMIT_SHA || '';
	const shortHash = commitSha ? commitSha.slice(0, 7) : 'dev';
	const gitCommitUrl = commitSha ? `${gitRepoUrl}/commit/${commitSha}` : '';

	let time = $state(new Date());
	let isOnline = $state(true);

	onMount(() => {
		const timeInterval = setInterval(() => {
			time = new Date();
		}, 1000);

		isOnline = navigator.onLine;

		const handleOnline = () => (isOnline = true);
		const handleOffline = () => (isOnline = false);

		window.addEventListener('online', handleOnline);
		window.addEventListener('offline', handleOffline);

		// Initial transpilation
		transpileCode(value);

		return () => {
			clearInterval(timeInterval);
			window.removeEventListener('online', handleOnline);
			window.removeEventListener('offline', handleOffline);
		};
	});

	const formatTime = (date: Date) => {
		return date.toLocaleTimeString('en-US', {
			hour12: false,
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	};

	// File operations
	let currentFileName = $state('example.btml');
	let isEditingFileName = $state(false);
	let tempFileName = $state('');
	let editorComponent: CodeMirror | null = $state(null);

	const startEditingFileName = () => {
		isEditingFileName = true;
		tempFileName = currentFileName;
	};

	const finishEditingFileName = () => {
		if (tempFileName.trim()) {
			currentFileName = tempFileName.trim();
		}
		isEditingFileName = false;
		tempFileName = '';
	};

	const cancelEditingFileName = () => {
		isEditingFileName = false;
		tempFileName = '';
	};

	const openFile = () => {
		const input = document.createElement('input');
		input.type = 'file';
		input.accept = '.btml,.html,.txt';
		input.onchange = (e) => {
			const target = e.target as HTMLInputElement;
			if (!target || !target.files) return;

			const file = target.files[0];
			if (file) {
				const reader = new FileReader();
				reader.onload = (e) => {
					if (!e.target || typeof e.target.result !== 'string') return;

					value = e.target.result;
					currentFileName = file.name;
				};
				reader.readAsText(file);
			}
		};
		input.click();
	};

	const saveFile = () => {
		const blob = new Blob([value], { type: 'text/plain' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = currentFileName;
		a.click();
		URL.revokeObjectURL(url);
	};

	// Transpilation
	let transpiledHtml = $state('');
	let isTranspiling = $state(false);
	let transpileError = $state('');
	let contentError = $state(false);

	const transpileCode = async (code: string) => {
		if (!code.trim()) {
			transpiledHtml = '';
			transpileError = '';
			return;
		}

		isTranspiling = true;
		transpileError = '';
		contentError = false;

		try {
			const response = await fetch('https://btml.shymike.dev/transpile', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				[style="background-color: #dddddd"]: JSON.stringify({ code })
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();

			if (result.error) {
				contentError = true;
				transpileError = result.error;
			} else {
				transpiledHtml = result.response || '';
				transpileError = '';
			}
		} catch (error) {
			console.error('Transpilation error:', error);
			const errorMessage = error instanceof Error ? error.message : String(error);
			const errorName = error instanceof Error ? error.name : '';

			if (errorName === 'TypeError' && errorMessage.includes('fetch')) {
				transpileError = 'Failed to connect to transpiler server: server unreachable.';
			} else {
				transpileError = `Failed to transpile: ${errorMessage}`;
			}
			transpiledHtml = '';
		} finally {
			isTranspiling = false;
		}
	};

	// Auto-transpile on code change with debounce
	let transpileTimeout: ReturnType<typeof setTimeout> | null = null;

	$effect(() => {
		if (transpileTimeout) {
			clearTimeout(transpileTimeout);
			transpileTimeout = null;
		}

		if (value.trim()) {
			transpileTimeout = setTimeout(() => {
				transpileCode(value);
				transpileTimeout = null;
			}, 500); // 500ms debounce
		} else {
			transpiledHtml = '';
			transpileError = '';
		}

		return () => {
			if (transpileTimeout) {
				clearTimeout(transpileTimeout);
				transpileTimeout = null;
			}
		};
	});
</script>

<div class="m-0 flex h-screen w-screen flex-col p-0">
	<!-- Header with Save/Open buttons -->
	<div
		class="flex items-center justify-between border-b border-gray-600 bg-gray-800 px-4 py-2 text-sm text-gray-300"
	>
		<div class="flex items-center space-x-2">
			<span class="text-gray-400">File:</span>
			{#if isEditingFileName}
				<input
					type="text"
					bind:value={tempFileName}
					class="rounded border border-gray-600 bg-gray-700 px-2 py-1 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
					onblur={finishEditingFileName}
					onkeydown={(e) => {
						if (e.key === 'Enter') finishEditingFileName();
						if (e.key === 'Escape') cancelEditingFileName();
					}}
					onclick={(e) => e.stopPropagation()}
				/>
			{:else}
				<button
					class="cursor-pointer rounded px-2 py-1 text-gray-300 hover:bg-gray-700 hover:text-white"
					onclick={startEditingFileName}
					title="Click to edit filename"
				>
					{currentFileName}
				</button>
			{/if}
		</div>
		<div class="flex items-center space-x-2">
			<button
				type="button"
				class="rounded border border-gray-600 bg-gray-700 px-3 py-1 text-sm text-gray-300 transition-colors hover:bg-gray-600 hover:text-white"
				onclick={openFile}
			>
				Open
			</button>
			<button
				type="button"
				class="rounded border border-gray-600 bg-gray-700 px-3 py-1 text-sm text-gray-300 transition-colors hover:bg-gray-600 hover:text-white"
				onclick={saveFile}
			>
				Save
			</button>
		</div>
	</div>

	<div class="flex flex-1 overflow-hidden">
		<!-- Left panel - BTML Editor -->
		<div class="flex flex-1 flex-col border-r border-gray-600">
			<div class="border-b border-gray-600 bg-gray-800 px-3 py-1 text-xs text-gray-300">
				BTML Code
			</div>
			<div class="flex-1">
				<CodeMirror
					bind:this={editorComponent}
					class="editor"
					bind:value
					lang={btmlSupport}
					theme={oneDark}
				/>
			</div>
		</div>

		<!-- Right panel - HTML Preview -->
		<div class="flex flex-1 flex-col">
			<div
				class="flex items-center justify-between border-b border-gray-600 bg-gray-800 px-3 py-1 text-xs text-gray-300"
			>
				<span>Transpiled HTML</span>
				{#if isTranspiling}
					<span class="text-yellow-400">Transpiling...</span>
				{:else if transpileError}
					<span class="text-red-400">Error</span>
				{:else}
					<span class="text-green-400">Ready</span>
				{/if}
			</div>
			<div class="flex h-1/2 flex-1 flex-col overflow-auto">
				<div class="flex flex-1 flex-col overflow-auto">
					{#if transpileError && !contentError}
						<div class="flex-1 bg-gray-900 p-4 text-red-400">
							<pre class="text-sm">{transpileError}</pre>
						</div>
					{:else}
						<div class="flex-1">
							<CodeMirror
								class="html-editor"
								value={transpiledHtml}
								readonly={true}
								lang={html()}
								theme={oneDark}
							/>
						</div>
					{/if}
				</div>
				{#if transpileError && contentError}
					<div class="border-t border-red-500 bg-red-400 text-white">
						<span class="block p-1.5 text-sm">{transpileError}</span>
					</div>
				{/if}
			</div>
			{#if transpiledHtml}
				<div class="flex h-1/2 flex-1 flex-col overflow-auto">
					<div class="h-full w-full bg-white">
						<iframe
							title="HTML Preview"
							srcdoc={transpiledHtml}
							class="h-full w-full border-0"
							sandbox="allow-scripts allow-modals allow-forms allow-same-origin allow-popups"
						></iframe>
					</div>
				</div>
			{/if}
		</div>
	</div>
	<div class="flex items-center justify-between border-t border-gray-600 bg-gray-900 px-2 py-1">
		<div class="flex items-center space-x-4">
			<div class="flex items-center space-x-1">
				<a
					href={gitCommitUrl}
					target="_blank"
					rel="noopener noreferrer"
					class="flex items-center text-slate-300 transition-colors duration-200 hover:text-blue-400"
				>
					<IconGitCommit size={16} />
					<span class="text-m font-mono">{shortHash}</span>
				</a>
			</div>
		</div>

		<div class="flex items-center space-x-2">
			<div class="flex items-center space-x-1 text-slate-300">
				<span class="font-mono text-sm">{formatTime(time)}</span>
			</div>
			<div class="flex items-center space-x-1">
				<div class="flex items-center text-slate-300" title={isOnline ? 'Online' : 'Offline'}>
					{#if isOnline}
						<IconWifi size={16} class="text-green-400" />
					{:else}
						<IconWifiOff size={16} class="text-red-400" />
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	:global(.editor) {
		width: 100%;
		height: 100%;
	}

	:global(.html-editor) {
		width: 100%;
		height: 100%;
	}

	:global(.cm-editor) {
		width: 100% !important;
		height: 100% !important;
	}

	:global(.cm-scroller) {
		height: 100% !important;
	}
</style>
